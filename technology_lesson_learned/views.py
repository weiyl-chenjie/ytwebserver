from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required  # 权限
# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.contrib import auth
from django.contrib.auth.models import Group

from django.conf import settings
from .models import Article, Customer
from .forms import LoginForm


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect('/technology_lesson_learned')
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)


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


def articles_with_customer(request, customer):
    print('进入articles_with_customer')
    articles_all_list = Article.objects.filter(project_info__customer_name=customer)
    context = get_blog_list_common_data(request, articles_all_list)
    return render(request, 'technology_lesson_learned/articles_with_customer.html', context)


def articles_with_project_number(request, project_number):
    articles_all_list = Article.objects.filter(project_info__project_number=project_number)
    context = get_blog_list_common_data(request, articles_all_list)
    context['articles_to_show_first'] = articles_all_list.first()
    return render(request, 'technology_lesson_learned/articles_with_project_number.html', context)


def articles_with_date(request, year, month):
    articles_all_list = Article.objects.filter(created_date__year=year, created_date__month=month)
    context = get_blog_list_common_data(request, articles_all_list)
    context['articles_with_date'] = '%s年%s月' % (year, month)
    return render(request, 'technology_lesson_learned/articles_with_date.html', context)


@login_required(login_url='/admin/login/')# 增加访问权限
def index(request):
    context = {}
    # 查询所有文章
    articles_all_list = Article.objects.all().order_by('-created_date')
    list(articles_all_list)  # 执行查询，后面直接用all_articles将不再查询数据库，否则每次使用all_articles都会查询数据库
    context = get_blog_list_common_data(request, articles_all_list)

    return render(request, 'technology_lesson_learned/index.html', context)
