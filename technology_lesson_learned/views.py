from django.shortcuts import render
from django.contrib.auth.decorators import login_required  # 权限
# Create your views here.


@login_required(login_url='/admin/login/')# 增加访问权限
def index(request):
    pass
