from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'Painting'

urlpatterns = [
    path('', views.index, name='index'),  # 默认页面
    path('painting_fpy_day_view/<date>/', views.painting_fpy_day_view, name='painting_fpy_day_view'),
    path('monthly/<date>/', views.monthly, name='monthly'),
]
