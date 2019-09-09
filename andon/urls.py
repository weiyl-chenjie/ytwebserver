from django.urls import path
from . import views

app_name = 'andon'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/', views.detail, name='detail'),
    path('detail/daily/<menu_id>/<date>/', views.detail_daily, name='detail_daily'),

    path('monthly/<int:menu_id>/<date>/', views.monthly, name='monthly'),

    path('line_stop/', views.line_stop, name='line_stop'),
    path('line_stop/date/<int:year>/<int:month>/<mps_or_line_stop>/', views.group_by_date, name='group_by_date'),
    path('line_stop/date/<int:year>/<int:month>/<project>/<production_line>/<mps_or_line_stop>/',
         views.group_by_date_production_line, name='group_by_date_production_line'),
    path('line_stop/production_line/<project>/<production_line>/<mps_or_line_stop>/',
         views.group_by_production_line, name='group_by_production_line'),
    path('line_stop/production_line/<project>/<production_line>/<int:year>/<int:month>/<mps_or_line_stop>/',
         views.group_by_production_line_date, name='group_by_production_line_date'),

    path('get_echarts_data/', views.get_echarts_data, name='get_echarts_data'),
]
