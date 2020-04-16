from django.contrib import admin

# Register your models here.
from .models import Customer, ProjectNumber, Article


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name',)
    ordering = ('customer_name',)


@admin.register(ProjectNumber)
class ProjectNumberAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'project_number')
    ordering = ('customer_name', 'project_number')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_info', 'created_date', 'last_updated_date', 'is_delete')
    ordering = ('-created_date',)
