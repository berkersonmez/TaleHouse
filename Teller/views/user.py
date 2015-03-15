from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect
from django.utils.text import slugify
from Teller.models import Profile
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from Teller.forms import UserLoginForm, UserAddForm, UserSearchForm
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext as _


def user_list(request):
    if not request.user.is_authenticated():
        return redirect('user_add')
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
        return redirect('user_add')
    if user_username is None:
        return redirect('error_info', _('An error occured'))
    try:
        profile = Profile.objects.get(slug=user_username)
    except Profile.DoesNotExist:
        return redirect('error_info', _('User not found'))
    context = {'profile_user': profile, 'profile_tales': profile.tales.filter(is_published=True)}
    return render_with_defaults(request, 'Teller/user_profile.html', context)


def user_add(request):
    if request.user.is_authenticated():
        return redirect('error_info', _('Already registered user'))
    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            # slug = slugify(username)
            user = User.objects.create_user(username, email, password)
            if user is None:
                return redirect('error_info', _('An error occured'))
            # Changed profile to be created on post_save signal
            # profile = Profile.objects.create(user=user, slug=slug)
            user = authenticate(username=username, password=password)
            if user is None or not user.is_active:
                return redirect('error_info', _('An error occured'))
            login(request, user)
            return redirect('index')
    else:
        form = UserAddForm()
    context = {'user_add_form': form}
    return render_with_defaults(request, 'Teller/user_add.html', context)


def user_login(request):
    if request.user.is_authenticated():
        return redirect('error_info', _('Already registered user'))
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
                    return redirect('error_info', _('User is disabled'))
            else:
                return redirect('error_info', _('Username or password is wrong'))
    return redirect('error_info', _('Invalid request'))


def user_logout(request):
    if not request.user.is_authenticated():
        return redirect('user_add')
    logout(request)
    return redirect('index')


def user_follow(request, target_username):
    if not request.user.is_authenticated():
        return redirect('user_add')
    profile = Profile.objects.get(user__id=request.user.id)
    if profile.user.username == target_username:
        return redirect('error_info', _('That makes no sense'))
    try:
        target = Profile.objects.get(slug=target_username)
    except Profile.DoesNotExist:
        return redirect('error_info', _('User not found'))
    if profile.is_following(target):
        profile.followed_users.remove(target)
    else:
        profile.followed_users.add(target)
    return redirect('user_profile', target.slug)