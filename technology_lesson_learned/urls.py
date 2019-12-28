from django.urls import path
from . import views

app_name = 'technology_lesson_learned'

urlpatterns = [
    path('', views.index, name='index'),
    path('customer/<customer>', views.articles_with_customer, name='articles_with_customer'),
    path('project_number/<project_number>', views.articles_with_project_number, name='articles_with_project_number'),
    path('date/<int:year>/<int:month>', views.articles_with_date, name='articles_with_date'),
    path('article/<int:article_pk>', views.article_detail, name='article_detail'),
    path('login/', views.login, name='login'),
]
