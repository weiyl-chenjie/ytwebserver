from django.contrib import admin

from .models import Menu, Mps, History, Maintainers, Managers, LineStop
# Register your models here.


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'production_line', 'product', 'ip', 'is_stop')
    ordering = ('project', 'production_line')


@admin.register(Mps)
class MpsAdmin(admin.ModelAdmin):
    list_display = ('id', 'menu_info', 'plan_outputs', 'workers', 'start_time', 'end_time', 'plc_ip')


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'mps_info', 'actual_outputs', 'input_datetime')


@admin.register(LineStop)
class LineStopAdmin(admin.ModelAdmin):
    list_display = ('id', 'menu_info', 'maintainer', 'reason', 'solution', 'start_time', 'end_time', 'line_stopping')


@admin.register(Maintainers)
class MaintainersAdmin(admin.ModelAdmin):
    list_display = ('name', 'mailbox')