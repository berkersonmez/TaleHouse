from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from django.core import validators
from Teller.models import Language, TalePart, Tale


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
    tale = forms.ModelChoiceField(queryset=Tale.objects.all(), required=True)
    name = forms.CharField(label=_('Name'))
    content = forms.CharField(widget=CKEditorWidget(), label=_('Content'))
    is_active = forms.BooleanField(label=_('Is active?'), required=False, initial=True)
    poll_end_date = forms.SplitDateTimeField(required=False)

    def __init__(self, user=None, *args, **kwargs):
        super(TalePartForm, self).__init__(*args, **kwargs)
        if not user is None:
            self.fields['tale'].queryset = Tale.objects.filter(user=user)


class TaleAddForm(forms.Form):
    name = forms.CharField(label=_('Tale Name'),
                           validators=[
                               validators.MinLengthValidator(3),
                               validators.MaxLengthValidator(200)
                           ])
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=True)
    is_poll_tale = forms.BooleanField(initial=False, required=False)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and Tale.objects.filter(name=name).count() > 0:
            raise forms.ValidationError("There is another tale with the same name.")
        return name
