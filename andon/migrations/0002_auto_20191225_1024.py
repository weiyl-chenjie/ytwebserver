# Generated by Django 2.2.5 on 2019-12-25 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('andon', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linestop',
            name='end_time',
            field=models.DateTimeField(verbose_name='结束停线'),
        ),
        migrations.AlterField(
            model_name='linestop',
            name='start_time',
            field=models.DateTimeField(verbose_name='开始停线'),
        ),
    ]