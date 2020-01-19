from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'technology_lesson_learned'

urlpatterns = [
    path('', views.index, name='index'),  # 默认页面
    path('customer/<customer>', views.articles_with_customer, name='articles_with_customer'),  # 按客户分类
    path('project_number/<project_number>', views.articles_with_project_number, name='articles_with_project_number'),  # 按项目号分类
    path('date/<int:year>/<int:month>', views.articles_with_date, name='articles_with_date'),  # 按日期分类
    path('article/<int:article_pk>', views.article_detail, name='article_detail'),  # 文章详情
    # 搜索的实现
    url(r'^search/', views.MySearchView(), name='haystack_search'),
]
