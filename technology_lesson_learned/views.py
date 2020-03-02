from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required  # 权限
# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.contrib import auth
from django.contrib.auth.models import Group

from django.conf import settings

# 第三方模块
from haystack.views import SearchView
from ytwebserver.settings import HAYSTACK_SEARCH_RESULTS_PER_PAGE

# 自己的模块
from .models import Article, Customer


class MySearchView(SearchView):
    def build_page(self):
        print('进入搜索页面：')
        # 分页重写
        context = super(MySearchView, self).extra_context()  # 继承自带的context
        try:
            page_no = int(self.request.GET.get('page', 1))
        except Exception:
            return HttpResponse("Not a valid number of page.")
        if page_no < 1:
            return HttpResponse("Page should be 1 or greater.")
        a = []
        for i in self.results:
            a.append(i.object)
        paginator = Paginator(a, HAYSTACK_SEARCH_RESULTS_PER_PAGE)
        page = paginator.page(page_no)
        print('搜索的文章:', page)
        return paginator, page

    def extra_context(self):
        context = super(MySearchView, self).extra_context  # 继承自带的context
        context['title'] = '搜索'
        return context


def user_is_authenticated(request):
    # 返回值：1代表有权限，-1代表没有权限，-2代表未登陆
    user = request.user
    if user.is_authenticated:  # 如果已登录
        app_groups = ['technology_lesson_learned_user', 'technology_lesson_learned_admin']  # 有权限查看该页面的组
        user_group_set = user.groups.all()  # 获取该用户所在的所有组
        user_group_list = [group.name for group in user_group_set]  # 把组由Group类型变成list元素
        has_permission = list(set(app_groups) & set(user_group_list))  # 取app_groups和user_group_list的交集，如果不为空，则表示有权限查看
        if has_permission:
            return 1  # 1代表有权限
        else:
            return -1  # -1代表没有权限
    else:  # 如果未认证（未登录），跳转到登陆界面
        return -2  # -2代表未登陆


def get_blog_list_common_data(request, articles_all_list):
    paginator = Paginator(articles_all_list, settings.EACH_PAGE_NUMBER)  # 每2页进行分页
    page_num = request.GET.get('page', 1)  # 获取页面分页参数(GET请求)，获取当前是在哪个分页上
    page_of_articles = paginator.get_page(page_num)  # 获取该分页上包含的数据信息
    # print(page_of_articles)
    # 以当前分页数为中心的分页区间（该算法取5个页码），如果page_num=3,则page_range= [1, 2, 3, 4, 5]
    page_range = [x for x in range(int(page_num) - 2, int(page_num) + 3) if 0 < x <= paginator.num_pages]
    # print(page_range[0])
    if page_range[0] > 1:
        page_range.insert(0, '...')
        page_range.insert(0, 1)
    if page_range[-1] < paginator.num_pages:
        page_range.append('...')
        page_range.append(paginator.num_pages)

    # 获取日期归档对应的文章数量
    article_dates = Article.objects.dates('created_date', 'month', order='DESC')
    article_dates_dict = {}
    for article_date in article_dates:
        # print(article_date, article_dates)
        article_count = Article.objects.filter(created_date__year=article_date.year, created_date__month=article_date.month).count()
        article_dates_dict[article_date] = article_count

    context = {}
    context['page_of_articles'] = page_of_articles
    context['articles_to_show'] = Article.objects.filter(is_delete=False)

    # 先按照Customer分组，再统计Article里的文章数目
    context['customers'] = Customer.objects.annotate(article_count=Count('projectnumber__article'))
    # context['customers'] = Customer.objects.annotate(article_count=Count('customer_name'))
    # print(context['customers'])
    context['page_range'] = page_range
    context['article_dates'] = article_dates_dict
    return context


def article_detail(request, article_pk):
    if user_is_authenticated(request):
        article = get_object_or_404(Article, pk=article_pk)
        article_content_type = ContentType.objects.get_for_model(article)

        context = {}
        context['article'] = article
        context['previous_article'] = Article.objects.filter(created_date__lt=article.created_date).first()
        context['next_article'] = Article.objects.filter(created_date__gt=article.created_date).last()

        data = {}
        data['content_type'] = article_content_type.model
        data['article_id'] = article_pk
        response = render(request, 'technology_lesson_learned/article_detail.html', context)

        return response
    else:
        return redirect('/technology_lesson_learned/login/')


def articles_with_customer(request, customer):
    if user_is_authenticated(request):
        articles_all_list = Article.objects.filter(project_info__customer_name=customer)
        context = get_blog_list_common_data(request, articles_all_list)
        return render(request, 'technology_lesson_learned/articles_with_customer.html', context)
    else:
        return redirect('/technology_lesson_learned/login/')


def articles_with_project_number(request, project_number):
    if user_is_authenticated(request):
        articles_all_list = Article.objects.filter(project_info__project_number=project_number)
        context = get_blog_list_common_data(request, articles_all_list)
        context['articles_to_show_first'] = articles_all_list.first()
        return render(request, 'technology_lesson_learned/articles_with_project_number.html', context)
    else:
        return redirect('/technology_lesson_learned/login/')


def articles_with_date(request, year, month):
    if user_is_authenticated(request):
        articles_all_list = Article.objects.filter(created_date__year=year, created_date__month=month)
        context = get_blog_list_common_data(request, articles_all_list)
        context['articles_with_date'] = '%s年%s月' % (year, month)
        return render(request, 'technology_lesson_learned/articles_with_date.html', context)
    else:
        return redirect('/technology_lesson_learned/login/')


def index(request):
    context = {}
    context['path'] = request.get_full_path()
    res = user_is_authenticated(request)
    app_groups = ['technology_lesson_learned_user', 'technology_lesson_learned_admin']  # 有权限查看该页面的组
    user = request.user
    # print(user.first_name)
    if res == 1:  # 如果用户已登录(已认证)
        user_group_set = user.groups.all()  # 获取该用户所在的所有组
        user_group_list = [group.name for group in user_group_set]  # 把组由Group类型变成list元素
        has_permission = list(set(app_groups) & set(user_group_list))  # 取app_groups和user_group_list的交集，如果不为空，则表示有权限查看
        # print(has_permission)
        if has_permission:
            # 查询所有文章
            articles_all_list = Article.objects.all().order_by('-created_date')
            list(articles_all_list)  # 执行查询，后面直接用all_articles将不再查询数据库，否则每次使用all_articles都会查询数据库
            context = get_blog_list_common_data(request, articles_all_list)
            context['user'] = user
            return render(request, 'technology_lesson_learned/index.html', context)
        else:
            return render(request, 'error.html')
    elif res == -1:  # 如果没有权限
        return render(request, 'forbidden.html')
    elif res == -2:  # 如果未登陆
        return redirect('/login?from=technology_lesson_learned')

