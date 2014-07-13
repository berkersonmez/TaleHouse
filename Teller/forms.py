from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from django.core import validators
from django.utils import timezone
from Teller.models import Language, TalePart, Tale, TaleLink
from django.db.models import Q


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
    tale = forms.ModelChoiceField(queryset=Tale.objects.all(), required=True, to_field_name='slug')
    name = forms.CharField(label=_('Name'))
    content = forms.CharField(widget=CKEditorWidget(), label=_('Content'))
    is_active = forms.BooleanField(label=_('Is active?'), required=False, initial=True)
    poll_end_date = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(
            options={"format": "YYYY-MM-DD HH:mm", "pickSeconds": False}
        )
    )

    def __init__(self, user=None, tale=None, *args, **kwargs):
        super(TalePartForm, self).__init__(*args, **kwargs)
        if not user is None:
            self.fields['tale'].queryset = Tale.objects.filter(user=user)
        if not tale is None:
            self.fields['tale'].widget.attrs['readonly'] = True
            self.fields['tale'].widget.attrs['disabled'] = True

    def clean_name(self):
        name = self.cleaned_data.get("name")
        tale = self.cleaned_data.get("tale")
        if name and TalePart.objects.filter(name=name, tale=tale).count() > 0:
            raise forms.ValidationError("There is another tale part with the same name.")
        return name

    def clean_poll_end_date(self):
        poll_end_date = self.cleaned_data.get("poll_end_date")
        tale = self.cleaned_data.get("tale")
        if tale.is_poll_tale and not poll_end_date:
            raise forms.ValidationError("Poll tale parts should have poll end date values.")
        if poll_end_date and poll_end_date < timezone.now():
            raise forms.ValidationError("Poll end date should be a future date.")
        return poll_end_date


class TaleEditPartForm(TalePartForm):
    def __init__(self, user=None, tale=None, tale_part_name=None, tale_part=None, *args, **kwargs):
        super(TaleEditPartForm, self).__init__(user, tale, *args, **kwargs)
        self.tale_part_name = tale_part_name
        if not tale_part is None:
            self.fields['tale'].initial = tale.slug
            self.fields['name'].initial = tale_part.name
            self.fields['content'].initial = tale_part.content
            self.fields['is_active'].initial = tale_part.is_active
            self.fields['poll_end_date'].initial = tale_part.poll_end_date

    def clean_name(self):
        name = self.cleaned_data.get("name")
        tale = self.cleaned_data.get("tale")
        if name and name != self.tale_part_name and TalePart.objects.filter(name=name, tale=tale).count() > 0:
            raise forms.ValidationError("There is another tale part with the same name.")
        return name


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
        slug = slugify(name)
        if name and Tale.objects.filter(Q(name=name) | Q(slug=slug)).count() > 0:
            raise forms.ValidationError("There is another tale with the same name.")
        return name


class TaleLinkAddForm(forms.Form):
    action = forms.CharField(label=_('Action Name'),
                             validators=[
                                 validators.MinLengthValidator(3),
                                 validators.MaxLengthValidator(200)
                             ])
    source = forms.ModelChoiceField(queryset=TalePart.objects.all(), required=True)
    destination = forms.ModelChoiceField(queryset=TalePart.objects.all(), required=True)

    def __init__(self, tale=None, *args, **kwargs):
        super(TaleLinkAddForm, self).__init__(*args, **kwargs)
        self.tale = tale
        if not tale is None:
            self.fields['source'].queryset = TalePart.objects.filter(tale=tale)
            self.fields['destination'].queryset = TalePart.objects.filter(tale=tale)

    def clean_action(self):
        action = self.cleaned_data.get("action")
        if action and TaleLink.objects.filter(action=action, tale=self.tale).count() > 0:
            raise forms.ValidationError("There is another link with the same action text.")
        return action

    def clean_destination(self):
        source = self.cleaned_data.get("source")
        destination = self.cleaned_data.get("destination")
        if source == destination:
            raise forms.ValidationError("Destination cannot be the same as source.")
        return destination


class TaleLinkEditForm(TaleLinkAddForm):
    def __init__(self, tale=None, tale_link_action=None, tale_link=None, *args, **kwargs):
        super(TaleLinkEditForm, self).__init__(tale, *args, **kwargs)
        self.tale_link_action = tale_link_action
        if not tale_link is None:
            self.fields['source'].initial = tale_link.source.id
            self.fields['destination'].initial = tale_link.destination.id
            self.fields['action'].initial = tale_link.action

    def clean_action(self):
        action = self.cleaned_data.get("action")
        if action and action != self.tale_link_action and TaleLink.objects.filter(action=action,
                                                                                  tale=self.tale).count() > 0:
            raise forms.ValidationError("There is another link with the same action text.")
        return action