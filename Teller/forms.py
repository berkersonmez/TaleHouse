from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from django.core import validators


class UserLoginForm(forms.Form):
    username = forms.CharField(label=_('Username'))
    password = forms.CharField(widget=forms.PasswordInput(), label=_('Password'))


class UserAddForm(forms.Form):
    username = forms.CharField(label=_('Username'),
                               validators=[
                                   validators.MinLengthValidator(3),
                                   validators.MaxLengthValidator(20)
                               ])
    password = forms.CharField(widget=forms.PasswordInput(),
                               label=_('Password'),
                               validators=[
                                   validators.MinLengthValidator(6)
                               ])
    email = forms.EmailField(label=_('E-mail'))

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError("Username is already in use.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("E-mail is already in use.")
        return email


class TalePartForm(forms.Form):
    name = forms.CharField(label=_('Name'))
    content = forms.CharField(widget=CKEditorWidget(), label=_('Content'))