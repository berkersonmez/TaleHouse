from django import forms
from django.utils.translation import ugettext_lazy as _


class UserLoginForm(forms.Form):
    username = forms.CharField(label=_('Username'))
    password = forms.CharField(widget=forms.PasswordInput(), label=_('Password'))
