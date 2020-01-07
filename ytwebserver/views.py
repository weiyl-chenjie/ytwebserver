from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from .forms import LoginForm


def home(request):
    context = {}
   
    return render(request, 'index.html', context)


def user_info(request):
    context = {}
    context['user'] = request.user

    return render(request, 'user_info.html', context)


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            # print(request.GET.get('from'))
            return redirect('/' + request.GET.get('from') + '/')
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))