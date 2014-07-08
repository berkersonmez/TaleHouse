from django.shortcuts import redirect
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from Teller.forms import UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _


def user_add(request):
    return render_with_defaults(request, 'Teller/user_add.html', {})


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