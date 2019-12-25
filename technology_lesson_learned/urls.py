from django.urls import path
from . import views

app_name = 'technology_lesson_learned'

urlpatterns = [
    path('', views.index, name='index'),
]
