from django.shortcuts import render, redirect
from django.db.models import Max, Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.decorators import login_required

import datetime
import calendar
import math
import json

from .models import Menu, Mps, History, LineStop, Maintainers, Managers

# Create your views here.


# 获取分页信息
def get_data_paginator(request, data_to_paginator):
    # 使用Paginator需要引用from django.core.paginator import Paginator
    paginator = Paginator(data_to_paginator, settings.EACH_PAGE_NUMBER)  # 每2页进行分页
    page_num = request.GET.get('page', 1)  # 获取页面分页参数(GET请求)，获取当前是在哪个分页上
    page_of_data = paginator.get_page(page_num)  # 获取该分页上包含的数据信息
    # 以当前分页数为中心的分页区间（该算法取5个页码），如果page_num=3,则page_range= [1, 2, 3, 4, 5]
    page_range = [x for x in range(int(page_num) - 2, int(page_num) + 3) if 0 < x <= paginator.num_pages]
    # print(page_range[0])
    if page_range[0] > 1:
        page_range.insert(0, '...')
        page_range.insert(0, 1)
    if page_range[-1] < paginator.num_pages:
        page_range.append('...')
        page_range.append(paginator.num_pages)

    context = {}
    context['page_of_data'] = page_of_data
    context['page_range'] = page_range
    return context


# 按照日期和流水线分组
def get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, count_by):  # count_by表示按照哪个表的数据排序
    context = {}

    context = get_data_paginator(request, data_to_paginator)
    # 按照年、月分组，并计算每个月的次数
    records_group_by_dates = all_records.values('start_time__year', 'start_time__month').annotate(
        record_counts=Count('start_time')).order_by('-start_time__year', '-start_time__month')
    # print(records_dates_counts.query)

    # 按照项目流水线分组，并统计各组在"count_by"中的数据数量（count_by表示以Menu为外键的某个表）
    records_group_by_production_line = menu_records.annotate(record_counts=Count(count_by)).order_by('production_line')
    # print(records_group_by_production_line.query)
    # print('records_group_by_production_line', records_group_by_production_line)
    context['records_group_by_dates'] = records_group_by_dates
    context['records_group_by_production_line'] = records_group_by_production_line
    return context


# Andon默认主页
# @login_required(login_url='/admin/login/')# 增加访问权限
def index(request):
    # 查询所有生产计划信息
    all_records = Mps.objects.all().order_by('-start_time')
    menu_records = Menu.objects.values('project', 'production_line')
    list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
    data_to_paginator = all_records.order_by('-start_time')
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    products_all = Menu.objects.order_by('project', 'production_line')  # Menu中所有的产品([丰田320A高配、丰田320A低配、福特C490高配...]
    projects_all = Menu.objects.distinct('project').values_list('project', flat=True)  # 去重后的所有客户([福特、丰田.....]
    # 今天生产的项目
    projects_today = Mps.objects.filter(start_time__range=[today, tomorrow]).values_list('menu_info_id', flat=True)
    # 现在正在停线的项目
    projects_stopping = LineStop.objects.filter(line_stopping=True).values_list('menu_info', flat=True)

    context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'mps')
    context['date'] = today
    context['products_all'] = products_all
    context['projects_all'] = projects_all
    context['projects_today'] = projects_today
    context['projects_stopping'] = projects_stopping
    context['mps_or_line_stop'] = 'mps'
    return render(request, 'andon/index.html', context)


def detail(request, menu_id, date):
    pass


# 每日生产信息详情
def detail_daily(request, menu_id, date):
    context = {}
    echarts_elements = {}  # 存储返回前端给echarts的数据

    # 获得url传过来的参数
    # menu_id = request.GET.get('menu')
    # date = datetime.datetime.strptime(request.GET.get('date'), '%Y-%m-%d')  # 字符串转化为日期格式
    menu_id = menu_id
    date = datetime.datetime.strptime(date, '%Y-%m-%d')  # 字符串转化为日期格式

    previous_day = date - datetime.timedelta(days=1)  # 前一天
    next_day = date + datetime.timedelta(days=1)  # 后一天

    # 查询该日生产计划，如果查询集不为空，即存在生产计划,
    # 则将每个生产项目(同一装配线，可能分一、二、三多个班次生产)的记录处理后分别存放到echarts_elements中
    if Mps.objects.filter(start_time__range=[date, next_day], menu_info_id=menu_id).exists():
        # 查询andon_mps表中今日生产的menu_info_id为menu_id的所有项目
        mps_objects = Mps.objects.filter(start_time__range=[date, next_day], menu_info_id=menu_id)
        for mps_object in mps_objects:
            x_axis = [x for x in range(mps_object.start_time.hour, mps_object.end_time.hour+1)]  # 获取生产时间段的各个整点

            # 存储各个整点的计划产量(向上取整）
            series_plan_data = [math.ceil((mps_object.plan_outputs/len(x_axis))*(x_axis.index(x)+1)) for x in x_axis]

            series_actual_data = []  # 存储各个整点的实际产量

            # 查询时间段内，记录中的各个小时实际产量的最大值及该小时对应的整点,返回格式为：
            # <QuerySet [{'input_datetime__hour': 9, 'actual_outputs__max': 300},
            #            {'input_datetime__hour': 12, 'actual_outputs__max': 356}]>
            outputs = list(History.objects.filter(input_datetime__range=(mps_object.start_time, mps_object.end_time),
                                                  mps_info_id=mps_object.id).values('input_datetime__hour').annotate(Max('actual_outputs')))
            x_actual_axis = [x['input_datetime__hour'] for x in outputs]  # 获取outputs中的整点

            # 在计划生产的时间段内，每一个没有生产记录的小时，将其生产数量赋值为0
            for i in x_axis:
                if i not in x_actual_axis:
                    outputs.append({'input_datetime__hour': i, 'actual_outputs__max': 0})
            outputs = sorted(outputs, key=lambda output: output['input_datetime__hour'])  # 按照outputs各个字典元素的key值排序

            series_actual_data = [x['actual_outputs__max'] for x in outputs]  # 获取各个整点产量

            echarts_element = {'x_axis': x_axis, 'series_plan_data': series_plan_data,
                               'series_actual_data': series_actual_data, 'mark_line_data': mps_object.plan_outputs}
            echarts_elements[mps_object.id] = echarts_element

        context['mps_empty'] = False
    else:
        mps_objects = Mps.objects.none()  # 赋值为空查询集
        context['mps_empty'] = True

    # 查看今日停线记录
    if LineStop.objects.filter(Q(line_stopping=True, menu_info_id=menu_id) |
                               Q(start_time__range=[date, next_day], menu_info_id=menu_id)).exists():
        linestop_objects = LineStop.objects.filter(Q(line_stopping=True, menu_info_id=menu_id) |
                                                   Q(start_time__range=[date, next_day], menu_info_id=menu_id))
    else:
        linestop_objects = LineStop.objects.none()  # 赋值为空查询集

    menu_obj = Menu.objects.get(id=menu_id)  # 获得andon_menu表中id为menu_id的项目

    context['mps_objects'] = mps_objects  # 在detail.html中生成表格数据（包含了生产计划的信息）
    context['line_stop_objects'] = linestop_objects  # 在detail.html中生成表格数据（包含了停线记录的信息）
    context['echarts_elements'] = json.dumps(echarts_elements)  # echarts控件的数据源
    context['menu_obj'] = menu_obj  # 项目信息
    context['date'] = date
    context['prev_day'] = previous_day
    context['next_day'] = next_day

    return render(request, 'andon/detail_daily.html', context)


# 按月查看生产信息
def monthly(request, menu_id, date):
    context = {}
    date_list = []  # 传递给前端日历坐标系的数据
    # 获得url传过来的参数
    # menu_id = request.GET.get("menu")
    # print(menu_id)
    # date = datetime.datetime.strptime(request.GET.get("month"), "%Y-%m")  # 字符串转化为日期格式
    menu_id = menu_id
    date = datetime.datetime.strptime(date, "%Y-%m")  # 字符串转化为日期格式

    menu_obj = Menu.objects.get(id=menu_id)  # 获得menu_id对应的数据项

    mdays = calendar.monthrange(date.year, date.month)[1]  # 获取该月份的天数
    # python3.8.1中，把calendar模块的prevmonth和nextmonth函数修改为了_prevmonth和_nextmonth函数
    # prev_month = "-".join([str(x) for x in (calendar.prevmonth(date.year, date.month))])  # 上个月，字符串格式为2019-7
    # next_month = "-".join([str(x) for x in (calendar.nextmonth(date.year, date.month))])  # 下个月，字符串格式为2019-9
    prev_month = "-".join([str(x) for x in (calendar._prevmonth(date.year, date.month))])  # 上个月，字符串格式为2019-7
    next_month = "-".join([str(x) for x in (calendar._nextmonth(date.year, date.month))])  # 下个月，字符串格式为2019-9

    # 查询本月计划生产的menu_info_id为menu_id的所有项目,并按日期去重, 同理查询停线记录的信息
    month_range = [date, datetime.datetime.strptime(next_month, "%Y-%m")]
    mps = list(Mps.objects.filter(start_time__range=month_range, menu_info_id=menu_id).distinct("start_time__day").values("start_time"))
    line_stop = list(LineStop.objects.filter(start_time__range=month_range, menu_info_id=menu_id).distinct("start_time__day").values("start_time"))

    # 获得该月哪些天有生产计划（按天存储）, 同理获取该月哪些天有停线记录（按天存储）
    mps_date = [x['start_time'].day for x in mps]
    line_stop_date = [x['start_time'].day for x in line_stop]

    date_start_with = date.strftime('%Y-%m-')  # 格式化字符串，格式为2019-09-，留着后续添加在'天'的前方组成日期，格式为：2019-09-01。
    # 获取传送给前端日历坐标系的数据
    for i in range(1, mdays+1):  # 循环遍历该月的天数
        element = []
        if i < 10:
            element.append(date_start_with + '0' + str(i))
        else:
            element.append(date_start_with + str(i))
        if i in mps_date:
            element.append('有生产')
        else:
            element.append('无生产')
        if i in line_stop_date:
            element.append('有停线')

        date_list.append(element)

    context['prev_month'] = prev_month
    context['next_month'] = next_month
    context['date_list'] = json.dumps(date_list)
    context['calendar_range'] = json.dumps(date.strftime('%Y-%m'))  # 告诉前端日历坐标系，要显示哪个年月的数据
    context['this_month'] = date
    context['menu_obj'] = menu_obj
    return render(request, 'andon/monthly.html', context)


def line_stop(request):
    # today = datetime.date.today()
    # seven_days_before = today - datetime.timedelta(days=7)
    # tomorrow = today + datetime.timedelta(days=1)

    # # 查询7天前至今天的所有停线信息
    # seven_days_records = LineStop.objects.filter(start_time__range=[seven_days_before, tomorrow])

    # 查询所有停线信息
    all_records = LineStop.objects.all()
    list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
    data_to_paginator = all_records.order_by('-start_time')
    menu_records = Menu.objects.values('project', 'production_line')

    context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'linestop')  # 其它给context赋值的语句应放在该句后面，以免被覆盖
    context['mps_or_line_stop'] = 'line_stop'  # 查看的是生产计划信息还是停线信息
    context['records'] = all_records

    return render(request, 'andon/line_stop.html', context)


def group_by_date(request, year, month, mps_or_line_stop):
    if mps_or_line_stop == 'mps':
        all_records = Mps.objects.filter(start_time__year=year, start_time__month=month).order_by(
            '-start_time')
        menu_records = Menu.objects.values('project', 'production_line').filter(mps__start_time__year=year,
                                                                                mps__start_time__month=month)
        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
        data_to_paginator = all_records.order_by('-start_time')
        # 其它给context赋值的语句应放在该句后面，以免被覆盖
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'mps')
        context['title'] = str(year) + '年' + str(month) + '月' + '生产计划信息'
    elif mps_or_line_stop == 'line_stop':
        # 查询所有停线信息
        all_records = LineStop.objects.filter(start_time__year=year, start_time__month=month)
        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
        data_to_paginator = all_records.order_by('-start_time')
        menu_records = Menu.objects.values('project', 'production_line').filter(linestop__start_time__year=year,
                                                                                linestop__start_time__month=month)
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'linestop')  # 其它给context赋值的语句应放在该句后面，以免被覆盖
        context['title'] = str(year) + '年' + str(month) + '月' + '停线信息'

    context['year'] = year
    context['month'] = month
    context['mps_or_line_stop'] = mps_or_line_stop  # 查看的是生产计划信息还是停线信息
    context['records'] = all_records

    return render(request, 'andon/group_by_date.html', context)


def group_by_date_production_line(request, year, month, project, production_line, mps_or_line_stop):
    if mps_or_line_stop == 'mps':
        # all_mps_records用于"按日期归档"
        # 获得该项目的所有生产计划，返回前端，用在"按日期归档"中
        all_records = Mps.objects.filter(start_time__year=year, start_time__month=month,
                                         menu_info__project=project,
                                         menu_info__production_line=production_line).order_by('-start_time')
        # menu_records用于"按流水线归档"，查询出该项目在该日期里的数据，各自对应的menu数据，留作后面计数用
        # 这里的效果：在该页面下点击，"按流水线归档"的数据不变，而下方的"按日期归档"则变为该项目当前日期的数量
        menu_records = Menu.objects.values('project', 'production_line').filter(
            # production_line=production_line,
            # project=project,
            mps__start_time__year=year,
            mps__start_time__month=month
        )

        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
        data_to_paginator = all_records.order_by('-start_time')
        # 其它给context赋值的语句应放在该句后面，以免被覆盖
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'mps')
        context['title'] = str(year) + '年' + str(month) + '月' + project + production_line + '生产计划信息'
    elif mps_or_line_stop == 'line_stop':
        all_records = LineStop.objects.filter(start_time__year=year, start_time__month=month,
                                              menu_info__project=project,
                                              menu_info__production_line=production_line).order_by('-start_time')
        menu_records = Menu.objects.values('project', 'production_line').filter(
                                                                                # production_line=production_line,
                                                                                # project=project,
                                                                                linestop__start_time__year=year,
                                                                                linestop__start_time__month=month
                                                                                )
        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
        data_to_paginator = all_records.order_by('-start_time')
        # 其它给context赋值的语句应放在该句后面，以免被覆盖
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'linestop')
        context['title'] = str(year) + '年' + str(month) + '月' + project + production_line + '停线信息'

    context['year'] = year
    context['month'] = month
    context['project'] = project
    context['production_line'] = production_line
    context['mps_or_line_stop'] = mps_or_line_stop  # 查看的是生产计划信息还是停线信息
    context['records'] = all_records

    return render(request, 'andon/group_by_date.html', context)


def group_by_production_line(request, project, production_line, mps_or_line_stop):
    if mps_or_line_stop == 'mps':
        all_records = Mps.objects.filter(menu_info__project=project, menu_info__production_line=production_line)
        menu_records = Menu.objects.values('project', 'production_line').filter(project=project,
                                                                                production_line=production_line)
        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
        data_to_paginator = all_records.order_by('-start_time')
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'mps')
        context['title'] = project + production_line + '生产计划信息'
    elif mps_or_line_stop == 'line_stop':
        # 查询所有停线信息
        all_records = LineStop.objects.filter(menu_info__project=project, menu_info__production_line=production_line)
        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库

        menu_records = Menu.objects.values('project', 'production_line').filter(project=project,
                                                                                production_line=production_line)
        data_to_paginator = all_records.order_by('-start_time')
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'linestop')
        context['title'] = project + production_line + '停线信息'

    records_group_by_production_line = all_records.filter(menu_info__project=project,
                                                                    menu_info__production_line=production_line)
    context['project'] = project
    context['production_line'] = production_line
    context['mps_or_line_stop'] = mps_or_line_stop
    context['records'] = records_group_by_production_line
    return render(request, 'andon/group_by_production_line.html', context)


def group_by_production_line_date(request, project, production_line, year, month, mps_or_line_stop):
    if mps_or_line_stop == 'mps':
        # all_mps_records用于"按日期归档"
        # 获得该项目的所有生产计划，返回前端，用在"按日期归档"中
        # 这里的效果：在该页面下点击，"按日期归档"数据不变，而上方的"按流水线归档"则变为该项目当前日期的数量
        all_records = Mps.objects.filter(menu_info__project=project, menu_info__production_line=production_line)
        # start_time__year=year, start_time__month=month)
        # menu_records用于"按流水线归档"，查询出该项目在该日期里的数据，各自对应的menu数据，留作后面计数用
        menu_records = Menu.objects.values('project', 'production_line').filter(project=project,
                                                                                production_line=production_line,
                                                                                mps__start_time__year=year,
                                                                                mps__start_time__month=month)
        # print(menu_records)
        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
        data_to_paginator = all_records.filter(start_time__year=year, start_time__month=month).order_by('-start_time')
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'mps')
        context['title'] = str(year) + '年' + str(month) + '月' + project + production_line + '生产计划信息'
    elif mps_or_line_stop == 'line_stop':
        # all_mps_records用于"按日期归档"
        # 获得该项目的所有生产计划，返回前端，用在"按日期归档"中，效果：在该页面下点击按日期归档，日期数据不变，而上方的"按流水线归档"则变为该项目当前日期的数量
        all_records = LineStop.objects.filter(menu_info__project=project, menu_info__production_line=production_line)
                                             # start_time__year=year, start_time__month=month)
        # menu_records用于"按流水线归档"，查询出该项目在该日期里的数据，各自对应的menu数据，留作后面计数用
        menu_records = Menu.objects.values('project', 'production_line').filter(project=project,
                                                                                production_line=production_line,
                                                                                linestop__start_time__year=year,
                                                                                linestop__start_time__month=month)
        # print('menu_records', menu_records)
        list(all_records)  # 执行查询，后面直接用records将不再查询数据库，否则每次使用records都会查询数据库
        data_to_paginator = all_records.filter(start_time__year=year, start_time__month=month).order_by('-start_time')
        context = get_records_group_by_date_or_production_line(request, all_records, data_to_paginator, menu_records, 'linestop')
        context['title'] = str(year) + '年' + str(month) + '月' + project + production_line + '停线信息'


    context['year'] = year
    context['month'] = month
    context['project'] = project
    context['production_line'] = production_line
    context['mps_or_line_stop'] = mps_or_line_stop
    context['records'] = all_records.filter(start_time__year=year, start_time__month=month)  # 该项目当前日期的数据

    return render(request, 'andon/group_by_production_line.html', context)


@csrf_exempt
def get_echarts_data(request):
    data = {}
    mps_id = request.POST['mps_id']

    mps_object = Mps.objects.get(id=mps_id)

    time_range_start = mps_object.start_time.hour
    time_range_end = mps_object.start_time.hour + math.ceil((mps_object.end_time - mps_object.start_time).total_seconds()/3600)
    print(time_range_end)
    x_axis = [x for x in range(time_range_start, time_range_end)]  # 获取生产时间段的各个整点

    x_axis = [x if x < 24 else x - 24 for x in x_axis]  # 对超过24点的进行处理

    # 存储各个整点的计划产量(向上取整）
    series_plan_data = [math.ceil((mps_object.plan_outputs / len(x_axis)) * (x_axis.index(x) + 1)) for x in x_axis]

    # 存储送给bootstrap-table的数据
    # 格式：[{'actual_outputs': 1, 'input_datetime': 2020-03-20 08:49:17.813583},
    #       {'actual_outputs': 100, 'input_datetime': 2020-03-20 08:59:17.956534}]
    bootstrap_table_data = []

    # 查询时间段内，记录中的各个小时实际产量的最大值及该小时对应的整点,返回格式为：
    # <QuerySet [{'input_datetime__hour': 9, 'actual_outputs__max': 300},
    #            {'input_datetime__hour': 12, 'actual_outputs__max': 356}]>
    outputs = list(History.objects.filter(input_datetime__range=(mps_object.start_time, mps_object.end_time),
                                          mps_info_id=mps_object.id).values('input_datetime__hour').annotate(
        Max('actual_outputs')))
    print(outputs)
    outputs_dic_temp = {x['input_datetime__hour']: x['actual_outputs__max'] for x in outputs}  # 字典的形式，获取outputs中整点对应的实际产量

    outputs_dic = {}
    for i in x_axis:  # x_axis里的时间是按照日期递增排序排列好的，因此，outputs_dict中的数值是按照时间依次排序的
        if i not in outputs_dic_temp.keys():
            outputs_dic[i] = 0  # 在计划生产的时间段内，每一个没有生产记录的小时，将其生产数量赋值为0
        else:
            outputs_dic[i] = outputs_dic_temp[i]
    print(outputs_dic)
    series_actual_data = [x[1] for x in outputs_dic.items()]  # 获取各个整点产量

    # project_info = mps_object.menu_info.project + mps_object.menu_info.production_line + mps_object.menu_info.product + \
    #                mps_object.start_time.strftime('%Y-%m-%d')
    project_info = mps_object.menu_info.project + mps_object.menu_info.production_line + mps_object.start_time.strftime('%Y-%m-%d')

    echarts_data = {'x_axis': x_axis, 'series_plan_data': series_plan_data,
                       'series_actual_data': series_actual_data, 'mark_line_data': mps_object.plan_outputs,
                    'project_info': project_info}

    outputs1 = list(History.objects.filter(input_datetime__range=(mps_object.start_time, mps_object.end_time), mps_info_id=mps_id))
    for i in outputs1:
        # 使用.replace(microsecond=0)去掉时间字段的毫秒
        bootstrap_table_data.append({'mps_id': i.mps_info_id, 'actual_outputs': i.actual_outputs, 'input_datetime': str(i.input_datetime.replace(microsecond=0))})

    data['status'] = 'SUCCESS'
    data['echarts_data'] = echarts_data
    data['bootstrap_table_data'] = bootstrap_table_data

    print(echarts_data)
    return JsonResponse(data)
