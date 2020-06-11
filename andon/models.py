from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.utils import timezone

import datetime

from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.


class Menu(models.Model):  # 项目、流水线信息
    project = models.CharField(max_length=20, verbose_name="项目归属")
    production_line = models.CharField(max_length=20, verbose_name="流水线")
    # product = models.CharField(max_length=20, verbose_name="产品")
    # assembly_number = models.CharField(max_length=20, verbose_name="总成号")
    ip = models.GenericIPAddressField(verbose_name="PLC的IP")
    is_stop = models.BooleanField(verbose_name='是否已停产', default=False)

    def __str__(self):
        # return self.project + self.production_line + self.product + '-' + self.assembly_number
        return self.project + self.production_line

    class Meta:
        app_label = "andon"
        # unique_together = (("project", "production_line", "product", "assembly_number"),)
        unique_together = (("project", "production_line"),)
        verbose_name = "项目总览"
        verbose_name_plural = verbose_name


class Mps(models.Model):  # 生产计划
    # 在数据库中的字段为menu_info_id
    menu_info = models.ForeignKey(Menu, on_delete=models.DO_NOTHING, verbose_name="项目信息")

    plan_outputs = models.PositiveIntegerField(verbose_name="计划产量")
    workers = models.PositiveIntegerField(verbose_name="生产人数")
    start_time = models.DateTimeField(verbose_name="开始生产时间")
    end_time = models.DateTimeField(verbose_name="结束生产时间")

    def __str__(self):
        # return self.menu_info.project + self.menu_info.production_line + self.menu_info.product + \
        #        " 计划产量" + str(self.plan_outputs) + " 生产人数" + str(self.workers) + \
        #        " 开始时间" + str(self.start_time) + " 结束时间" + str(self.end_time)
        return self.menu_info.project + self.menu_info.production_line + \
               " 计划产量" + str(self.plan_outputs) + " 生产人数" + str(self.workers) + \
               " 开始时间" + str(self.start_time) + " 结束时间" + str(self.end_time)
    def clean(self):
        if self.start_time > self.end_time:
            raise ValidationError({'start_time': _("开始时间不能晚于结束时间")})

    # 自定义的显示字段，在admin.py中可以像使用字段一样使用该函数。比如要显示plc_ip，可以使用list_display = ('plc_ip')
    # plc的ip
    def plc_ip(self):
        return self.menu_info.ip

    # 零件总成号
    # def assembly_number(self):
    #     return self.menu_info.assembly_number

    plc_ip.short_description = "PLC的IP"
    # assembly_number.short_description = "总成号"

    class Meta:
        app_label = "andon"
        verbose_name = "生产计划"
        verbose_name_plural = verbose_name


class History(models.Model):  # 生产记录
    # 在数据库中的字段为mps_info_id
    mps_info = models.ForeignKey(Mps, on_delete=models.DO_NOTHING, verbose_name="项目信息")
    actual_outputs = models.PositiveIntegerField()
    input_datetime = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        app_label = 'andon'
        verbose_name = '历史记录'
        verbose_name_plural = verbose_name


class Maintainers(models.Model):  # 停线维护人员
    name = models.CharField(verbose_name="姓名", max_length=10)
    mailbox = models.EmailField(verbose_name="邮箱")

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'andon'
        verbose_name = '维护人员'
        verbose_name_plural = verbose_name


class Managers(models.Model):  # 管理人员--系统异常时向其发送邮件提醒
    name = models.CharField(verbose_name="姓名", max_length=10)
    mailbox = models.EmailField(verbose_name="邮箱")

    class Meta:
        app_label = 'andon'
        verbose_name = 'Andon管理人员'
        verbose_name_plural = verbose_name


class LineStop(models.Model):  # 停线记录
    # 在数据中的字段为menu_info_id
    menu_info = models.ForeignKey(Menu, on_delete=models.DO_NOTHING, verbose_name="项目信息")
    maintainer = models.ForeignKey(Maintainers, on_delete=models.DO_NOTHING, verbose_name="维护人员")
    reason = RichTextUploadingField(verbose_name='停线原因', blank=True, null=True)
    solution = RichTextUploadingField(verbose_name='解决方案', blank=True, null=True)
    start_time = models.DateTimeField(verbose_name="开始停线")
    end_time = models.DateTimeField(verbose_name="结束停线")
    line_stopping = models.BooleanField(verbose_name="停线中", default=False)

    def clean(self):
        if self.start_time > self.end_time:
            raise ValidationError({'start_time': _("开始时间不能晚于结束时间")})

    class Meta:
        app_label = 'andon'
        verbose_name = '停线记录'
        verbose_name_plural = verbose_name


