# Generated by Django 2.2.5 on 2019-12-25 11:36

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Maintainers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='姓名')),
                ('mailbox', models.EmailField(max_length=254, verbose_name='邮箱')),
            ],
            options={
                'verbose_name': '维护人员',
                'verbose_name_plural': '维护人员',
            },
        ),
        migrations.CreateModel(
            name='Managers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='姓名')),
                ('mailbox', models.EmailField(max_length=254, verbose_name='邮箱')),
            ],
            options={
                'verbose_name': 'Andon管理人员',
                'verbose_name_plural': 'Andon管理人员',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(max_length=20, verbose_name='项目')),
                ('production_line', models.CharField(max_length=20, verbose_name='流水线')),
                ('product', models.CharField(max_length=20, verbose_name='产品')),
                ('ip', models.GenericIPAddressField(verbose_name='PLC的IP')),
                ('is_stop', models.BooleanField(default=False, verbose_name='是否已停产')),
            ],
            options={
                'verbose_name': '项目总览',
                'verbose_name_plural': '项目总览',
                'permissions': [('test_menu', '测试项目总览')],
                'unique_together': {('project', 'production_line', 'product')},
            },
        ),
        migrations.CreateModel(
            name='Mps',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_outputs', models.PositiveIntegerField(verbose_name='计划产量')),
                ('workers', models.PositiveIntegerField(verbose_name='生产人数')),
                ('start_time', models.DateTimeField(verbose_name='开始生产时间')),
                ('end_time', models.DateTimeField(verbose_name='结束生产时间')),
                ('menu_info', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='andon.Menu', verbose_name='项目信息')),
            ],
            options={
                'verbose_name': '生产计划',
                'verbose_name_plural': '生产计划',
            },
        ),
        migrations.CreateModel(
            name='LineStop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='停线原因')),
                ('solution', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='解决方案')),
                ('start_time', models.DateTimeField(verbose_name='开始停线')),
                ('end_time', models.DateTimeField(verbose_name='结束停线')),
                ('line_stopping', models.BooleanField(default=False, verbose_name='停线中')),
                ('maintainer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='andon.Maintainers', verbose_name='维护人员')),
                ('menu_info', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='andon.Menu', verbose_name='项目信息')),
            ],
            options={
                'verbose_name': '停线记录',
                'verbose_name_plural': '停线记录',
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actual_outputs', models.PositiveIntegerField()),
                ('input_datetime', models.DateTimeField(auto_now_add=True)),
                ('mps_info', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='andon.Mps', verbose_name='项目信息')),
            ],
            options={
                'verbose_name': '历史记录',
                'verbose_name_plural': '历史记录',
            },
        ),
    ]
