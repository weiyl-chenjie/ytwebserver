from django.shortcuts import render

import datetime
import calendar
import math
import json

# 第三方库
# import pyodbc
import pymssql
# Create your views here.


# 自定义类
class ODBC_MS:
    def __init__(self, SERVER, USERNAME, PASSWORD, DATABASE):
        # self.DRIVER = DRIVER
        self.SERVER = SERVER
        self.DATABASE = DATABASE
        self.USERNAME = USERNAME
        self.PASSWORD = PASSWORD
        self.PORT = PORT

    def __GetConnect(self):
        # if not self.DRIVER:
        #     raise (NameError, "no setting DRIVER info")
        self.conn = pymssql.connect(self.SERVER, self.USERNAME, self.PASSWORD, self.DATABASE)
        crsr = self.conn.cursor()
        if not crsr:
            raise (NameError, "connected failed!")
        else:
            return crsr

    def select_query(self, sql):
        crsr = self.__GetConnect()
        crsr.execute(sql)
        rows = crsr.fetchall()
        crsr.close()
        self.conn.close()
        return rows

    def update_query(self, sql):
        crsr = self.__GetConnect()
        crsr.execute(sql)
        self.conn.commit()
        crsr.close()
        self.conn.close()

    def insert_query(self, sql):
        crsr = self.__GetConnect()
        crsr.execute(sql)
        self.conn.commit()
        crsr.close()
        self.conn.close()


# DRIVER = '{SQL Server}'
SERVER = '192.168.0.2'
USERNAME = 'hufyt'
PASSWORD = 'hufyt'
DATABASE = 'pps_server'
PORT = 1433
# 创建数据库连接实例
odbc_ms = ODBC_MS(SERVER, USERNAME, PASSWORD, DATABASE)


def index(request):
    content = {}
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    content['today'] = today
    return render(request, 'Painting/index.html', content)


def painting_fpy_day_view(request, date):
    content = {}
    echarts_elements = {}  # 存储返回前端给echarts的数据
    x_axis = []
    y_axis = []
    bootstrap_table_data = []
    d_records_all = {}  # 按小时分组计算的所有件，key值为小时，value为该小时的总产量
    d_records_qualified = {}  # 按小时分组计算的合格件，key值为小时，value为该小时的合格件产量
    sum_records_all = 0  # 当日总产量（把各个小时的总产量相加）
    sum_records_qualified = 0  # 当日合格产量（把各个小时的合格量相加）

    # 获得url传过来的参数
    # menu_id = request.GET.get('menu')
    # date = datetime.datetime.strptime(request.GET.get('date'), '%Y-%m-%d')  # 字符串转化为日期格式
    date = datetime.datetime.strptime(date, '%Y-%m-%d')  # 字符串转化为日期格式
    prev_day = date - datetime.timedelta(days=1)  # 前一天
    next_day = date + datetime.timedelta(days=1)  # 后一天


    #  str(date)格式：2021-01-27 00:00:00
    # 数据查询：今天8：00之后，至明天8：00之前，比如查询2021-01-31的数据，2021-01-31 8：00：00<查询的时间<2021-02-01 8：00：00
    sql_all = f"""SELECT DATEPART(year,input_time), DATEPART(month,input_time), DATEPART(day,input_time), DATEPART(hour,input_time), SUM(Quantity)
                 FROM Painting_Production_Records
                 WHERE(Painting_Date = '{str(date).split(' ')[0]}')
                 GROUP BY DATEPART(year,input_time), DATEPART(month,input_time), DATEPART(day,input_time), DATEPART(hour,input_time)"""
    records_all = odbc_ms.select_query(sql_all)

    sql_qualified = f"""SELECT DATEPART(year,input_time), DATEPART(month,input_time), DATEPART(day,input_time), DATEPART(hour,input_time), SUM(Quantity)
                       FROM Painting_Production_Records
                       WHERE(Painting_Date = '{str(date).split(' ')[0]}')
                       AND (Defect = '00')
                       GROUP BY DATEPART(year,input_time), DATEPART(month,input_time), DATEPART(day,input_time), DATEPART(hour,input_time)"""
    records_qualified = odbc_ms.select_query(sql_qualified)
    print(records_qualified)

    for i in records_all:
        # 格式"yyyy-mm-dd hh"
        d_records_all[str(i[0]) + '-' + str(i[1]).zfill(2) + '-' + str(i[2]).zfill(2) + ' ' + str(i[3]).zfill(2)] = i[4]

    for i in records_qualified:
        d_records_qualified[str(i[0]) + '-' + str(i[1]).zfill(2) + '-' + str(i[2]).zfill(2) + ' ' + str(i[3]).zfill(2)] = i[4]

    print(d_records_all)

    for i in d_records_all.keys():
        if i not in d_records_qualified.keys():
            d_records_qualified[i] = 0

    d_records_all = sort_dict(**d_records_all)
    d_records_qualified = sort_dict(**d_records_qualified)
    print(d_records_qualified)

    fpy = {i: round(d_records_qualified[i] / d_records_all[i], 2) for i in d_records_all.keys() if d_records_all[i] != 0}
    for key, value in fpy.items():
        x_axis.append(key)
        y_axis.append(value)
        bootstrap_table_data.append({'hour':key, 'hourly_output_qualified':d_records_qualified[key], 'hourly_output':d_records_all[key]})
        sum_records_all = sum_records_all + d_records_all[key]
        sum_records_qualified = sum_records_qualified + d_records_qualified[key]

    echarts_elements['x_axis'] = x_axis  # echarts x轴坐标：按小时划分
    echarts_elements['y_axis'] = y_axis  # echarts y轴坐标：按每小时合格率划分
    if sum_records_all == 0:  # 如果没有生产记录
        echarts_elements['day_fpy'] = 0
    else:
        echarts_elements['day_fpy'] = round(sum_records_qualified / sum_records_all, 4)  # 日合格率

    if len(records_all) == 0:  # 如果没有生产数据, 则mps_empty置为真
        content['mps_empty'] = True
    else:
        content['mps_empty'] = False
    content['date'] = date
    content['prev_day'] = prev_day
    content['next_day'] = next_day
    content['sum_records_qualified'] = sum_records_qualified  # 合格的数量
    content['sum_records_all'] = sum_records_all  # 总产量
    content['echarts_elements'] = json.dumps(echarts_elements)  # echarts控件的数据源
    content['bootstrap_table_data'] = json.dumps(bootstrap_table_data)  # bootstraptable使用的数据
    return render(request, 'Painting/painting_fpy_day_view.html', content)


# 按月查看生产信息
def monthly(request, date):
    context = {}
    date_list = []  # 传递给前端日历坐标系的数据
    # 获得url传过来的参数
    # date = datetime.datetime.strptime(request.GET.get("month"), "%Y-%m")  # 字符串转化为日期格式
    date = datetime.datetime.strptime(date, "%Y-%m")  # 字符串转化为日期格式
    mdays = calendar.monthrange(date.year, date.month)[1]  # 获取该月份的天数
    # python3.8.1中，把calendar模块的prevmonth和nextmonth函数修改为了_prevmonth和_nextmonth函数
    # prev_month = "-".join([str(x) for x in (calendar.prevmonth(date.year, date.month))])  # 上个月，字符串格式为2019-7
    # next_month = "-".join([str(x) for x in (calendar.nextmonth(date.year, date.month))])  # 下个月，字符串格式为2019-9
    prev_month = "-".join([str(x) for x in (calendar._prevmonth(date.year, date.month))])  # 上个月，字符串格式为2019-7
    next_month = "-".join([str(x) for x in (calendar._nextmonth(date.year, date.month))])  # 下个月，字符串格式为2019-9

    # 每月数据，按天分组并取出最后一条数据
    sql_groupBy_day = f"""SELECT MAX(Painting_Date)
                         FROM Painting_Production_Records
                         WHERE (CONVERT(varchar(7), Painting_Date, 120) = '{str(date)[:7]}')
                         GROUP BY CONVERT(varchar(10), Painting_Date, 120)"""
    rows = odbc_ms.select_query(sql_groupBy_day)
    print(sql_groupBy_day)
    print(rows)
    # 获得该月哪些天有生产计划（按天存储）, 同理获取该月哪些天有停线记录（按天存储）
    # 借鉴的andon系统，这里不需要停线记录，所以停线记录为空
    mps_date = sorted([x[0].day for x in rows])
    line_stop_date = []

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
    return render(request, 'Painting/monthly.html', context)


# 自定义功能函数
def sort_dict(**kwargs):
    tmp = sorted(kwargs.items(), key = lambda d:d[0])
    kwargs.clear()
    for i in tmp:
        kwargs[i[0]] = i[1]
    return kwargs

