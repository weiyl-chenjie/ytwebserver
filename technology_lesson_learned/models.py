from django.db import models

# Create your models here.
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField


# 客户列表
class Customer(models.Model):
    # 客户名称
    customer_name = models.CharField(max_length=20, verbose_name='客户名称')

    def __str__(self):
        return self.customer_name

    def clean(self):
        reject = ['/', '\\']
        for i in reject:
            if i in self.customer_name:
                raise ValidationError({'customer_name': _("不能包含字符%s，请使用其它字符替代" % i)})

    class Meta:
        app_label = 'technology_lesson_learned'
        verbose_name = "客户列表"
        verbose_name_plural = verbose_name
        ordering = ('customer_name',)


# 项目号
class ProjectNumber(models.Model):
    # 客户名称
    customer_name = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, verbose_name='客户')
    # 项目号
    project_number = models.CharField(max_length=20, verbose_name='项目号')

    def __str__(self):
        return '%s:%s' % (self.customer_name, self.project_number)

    def clean(self):
        reject = ['/', '\\']
        for i in reject:
            if i in self.project_number:
                raise ValidationError({'project_number': _("不能包含字符%s，请使用其它字符替代" % i)})

    class Meta:
        app_label = 'technology_lesson_learned'
        verbose_name = "项目号"
        verbose_name_plural = verbose_name
        ordering = ('customer_name', 'project_number')


# technology_lesson_learned 文章
class Article(models.Model):
    # 文章标题
    title = models.CharField(max_length=30, verbose_name='标题')
    # 所属客户名称和项目号
    project_info = models.ForeignKey(ProjectNumber, on_delete=models.DO_NOTHING, verbose_name='客户及项目号')

    # 问题描述
    issue = RichTextUploadingField(verbose_name='问题描述')
    # 解决方案
    solution = RichTextUploadingField(verbose_name='解决方案')
    # 创建时间
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 最后修改时间
    last_updated_date = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    # 是否删除文章(True代表不显示文章,False代表正常显示文章)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return '<文章:%s>' % self.title

    class Meta:
        app_label = 'technology_lesson_learned'
        # unique_together = (("author", "title"),)
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ('-created_date',)