from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect
from Teller.models import Profile
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from Teller.forms import UserLoginForm, UserAddForm, UserSearchForm
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _


def user_list(request):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    page_no = 1
    username = ''
    if request.method == 'GET':
        if 'page' in request.GET:
            page_no = request.GET.get('page')
        form = UserSearchForm(request.GET)
        if form.is_valid():
            username = form.cleaned_data['username']
            users = Profile.objects.filter(user__username__contains=username)
        else:
            users = Profile.objects.all()
    else:
        users = Profile.objects.all()
        form = UserSearchForm()
    user_paginator = Paginator(users, 25)
    try:
        users_in_page = user_paginator.page(page_no)
    except PageNotAnInteger:
        users_in_page = user_paginator.page(1)
    except EmptyPage:
        users_in_page = user_paginator.page(user_paginator.num_pages)
    context = {'user_list_form': form,
               'username': username,
               'users_in_page': users_in_page,
               'page_no': page_no}
    return render_with_defaults(request, 'Teller/user_list.html', context)


def user_profile(request, user_username):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    if user_username is None:
        return redirect('error_info', 'An error occured')
    try:
        profile = Profile.objects.get(user__username=user_username)
    except Profile.DoesNotExist:
        return redirect('error_info', 'User not found')
    context = {'profile_user': profile, 'profile_tales': profile.tales.filter(is_published=True)}
    return render_with_defaults(request, 'Teller/user_profile.html', context)


def user_add(request):
    if request.user.is_authenticated():
        return redirect('error_info', 'Already registered user')
    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username, email, password)
            profile = Profile.objects.create(user=user)
            user = authenticate(username=username, password=password)
            if user is None or not user.is_active or profile is None:
                return redirect('error_info', 'An error occured')
            login(request, user)
            return redirect('index')
    else:
        form = UserAddForm()
    context = {'user_add_form': form}
    return render_with_defaults(request, 'Teller/user_add.html', context)


def user_login(request):
    if request.user.is_authenticated():
        return redirect('error_info', 'Already registered user')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
                else:
                    return redirect('error_info', 'User is disabled')
            else:
                return redirect('error_info', 'Username or password is wrong')
    return redirect('error_info', 'Invalid request')


def user_logout(request):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    logout(request)
    return redirect('index')