from django.contrib.auth.models import User
from django.shortcuts import redirect
from Teller.models import Profile
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from Teller.forms import UserLoginForm, UserAddForm
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _


def user_add(request):
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
    logout(request)
    return redirect('index')