# -*- coding: utf-8 -*-
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from ckeditor.widgets import CKEditorWidget
from django.core import validators
from django.utils import timezone
from parsley.decorators import parsleyfy
from Teller.models import Language, TalePart, Tale, TaleLink, TaleVariable, TaleLinkPrecondition, TaleLinkConsequence, \
    Profile
from django.db.models import Q
from captcha.fields import CaptchaField


@parsleyfy
class UserLoginForm(forms.Form):
    username = forms.CharField(label=ugettext_lazy('Username'))
    password = forms.CharField(widget=forms.PasswordInput(), label=ugettext_lazy('Password'))
    captcha = CaptchaField()


@parsleyfy
class UserSearchForm(forms.Form):
    username = forms.CharField(label=ugettext_lazy('Username'))


@parsleyfy
class UserAddForm(forms.Form):
    username = forms.CharField(label=ugettext_lazy('Username'),
                               validators=[
                                   validators.MinLengthValidator(3),
                                   validators.MaxLengthValidator(20)
                               ])
    password = forms.CharField(widget=forms.PasswordInput(),
                               label=ugettext_lazy('Password'),
                               validators=[
                                   validators.MinLengthValidator(6)
                               ])
    email = forms.EmailField(label=ugettext_lazy('E-mail'))

    captcha = CaptchaField()

    def clean_username(self):
        username = self.cleaned_data.get("username")
        slug = slugify(username)
        if username and User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError(_("Username is already in use."))
        if username and slug and Profile.objects.filter(slug=slug).count() > 0:
            raise forms.ValidationError(_("Username is already in use."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(_("E-mail is already in use."))
        return email


@parsleyfy
class TaleSearchForm(forms.Form):
    TYPE_CHOICES = (
        ('all', ugettext_lazy('Search all types')),
        ('normal', ugettext_lazy('Search normal tales')),
        ('poll', ugettext_lazy('Search poll tales'))
    )
    ORDER_BY_CHOICES = (
        ('rating', ugettext_lazy('Order by rating')),
        ('name', ugettext_lazy('Order by name')),
        ('date', ugettext_lazy('Order by date'))
    )
    LANGUAGE_CHOICES = (
        ('all', ugettext_lazy('Search all languages')),
        ('enUS', ugettext_lazy('English tales')),
        ('tr', ugettext_lazy('Turkish tales'))
    )
    tale_name = forms.CharField(label=ugettext_lazy('Tale name'), required=False)
    followed_user_tales = forms.BooleanField(label=ugettext_lazy('Followed users only'), required=False)
    type = forms.ChoiceField(label=ugettext_lazy('Tale type'), choices=TYPE_CHOICES, initial=TYPE_CHOICES[0][0],
                             required=True)
    order_by = forms.ChoiceField(label=ugettext_lazy('Order by'), choices=ORDER_BY_CHOICES,
                                 initial=ORDER_BY_CHOICES[0][0],
                                 required=True)
    language = forms.ChoiceField(label=ugettext_lazy('Language'), choices=LANGUAGE_CHOICES,
                                 initial=LANGUAGE_CHOICES[0][0],
                                 required=True)


@parsleyfy
class TalePartForm(forms.Form):
    tale = forms.ModelChoiceField(queryset=Tale.objects.all(), required=True, to_field_name='slug',
                                  help_text=ugettext_lazy(
                                      'Tales consist of tale parts. Select a tale to add this tale part to.'))
    name = forms.CharField(label=ugettext_lazy('Name'),
                           help_text=ugettext_lazy(
                               'Give a name to the tale part to recognize it easily. It will not be shown to '
                               'the readers automatically.'))
    content = forms.CharField(widget=CKEditorWidget(), label=ugettext_lazy('Content'),
                              help_text=ugettext_lazy(
                                  'Write the content of the tale part. Advance the story and prepare for the '
                                  'events that will lead to the next parts.'))
    is_active = forms.BooleanField(label=ugettext_lazy('Is active?'), required=False, initial=True,
                                   help_text=ugettext_lazy(
                                       'If a tale part is not active, the story will not progress at'
                                       ' that part. Use this to complete unfinished parts while not blocking'
                                       ' the whole story.'))
    poll_end_date = forms.DateTimeField(
        label=ugettext_lazy('Poll end date'),
        required=False,
        widget=DateTimePicker(
            options={"format": "YYYY-MM-DD HH:mm", "pickSeconds": False}
        ),
        help_text=ugettext_lazy(
            'Only applicible to poll tales. Poll tale parts stay open for community votes until poll end date. '
            'After that time, the story will advance according to the mostly voted part.')
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
            raise forms.ValidationError(_("There is another tale part with the same name."))
        return name

    def clean_poll_end_date(self):
        poll_end_date = self.cleaned_data.get("poll_end_date")
        tale = self.cleaned_data.get("tale")
        if tale and tale.is_poll_tale and not poll_end_date:
            raise forms.ValidationError(_("Poll tale parts should have poll end date values."))
        if poll_end_date and poll_end_date < timezone.now():
            raise forms.ValidationError(_("Poll end date should be a future date."))
        return poll_end_date


@parsleyfy
class TaleVariableAddForm(forms.Form):

    name = forms.CharField(label=ugettext_lazy('Name'), required=True,
                           help_text=ugettext_lazy(
                               'Tale variables let you create immersive choices and consequences. '
                               'Give a name to the tale variable to recognize it easily. It will not be shown to '
                               'the readers automatically.'))

    default_value = forms.IntegerField(label=ugettext_lazy('Default Value'),
                                       help_text=ugettext_lazy(
                                       'Give a starting value to this variable according to its purpose. '
                                       'For example, if this is "gold" you might want to start the player with '
                                       '200 gold and make them spend it throughout the story.'),
                                       required=True)

    def __init__(self, tale=None, *args, **kwargs):
        super(TaleVariableAddForm, self).__init__(*args, **kwargs)
        self.tale = tale

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and TaleVariable.objects.filter(name=name, tale=self.tale).count() > 0:
            raise forms.ValidationError(_("There is another variable with the same name."))
        return name

    def clean_default_value(self):
        default_value = self.cleaned_data.get("default_value")
        if default_value:
            try:
                int(default_value)
            except ValueError:
                raise forms.ValidationError(_("Default value should be an integer."))
            if int(default_value) > 2147483646 or int(default_value) < -2147483646:
                raise forms.ValidationError(_("Default value is invalid."))
        return default_value


@parsleyfy
class TaleVariableEditForm(TaleVariableAddForm):
    def __init__(self, tale=None, tale_variable_name=None, tale_variable=None, *args, **kwargs):
        super(TaleVariableEditForm, self).__init__(tale, *args, **kwargs)
        self.tale_variable_name = tale_variable_name
        if not tale_variable is None:
            self.fields['name'].initial = tale_variable.name
            self.fields['default_value'].initial = tale_variable.default_value

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and name != self.tale_variable_name and TaleVariable.objects.filter(name=name,
                                                                                    tale=self.tale).count() > 0:
            raise forms.ValidationError(_("There is another variable with the same name."))
        return name


@parsleyfy
class TalePreconditionAddForm(forms.Form):
    PRECONDITION_CHOICES = TaleLinkPrecondition.PRECONDITION_CHOICES

    tale_variable = forms.ModelChoiceField(label=ugettext_lazy('Variable'), queryset=TalePart.objects.all(), required=True,
                                           help_text=ugettext_lazy('If this variable does not yield the condition, '
                                                                   'the link will not be available to choose for the '
                                                                   'reader.'))

    condition = forms.ChoiceField(label=ugettext_lazy('Condition'), choices=PRECONDITION_CHOICES,
                                  initial=PRECONDITION_CHOICES[0][0],
                                  required=True)

    value = forms.IntegerField(label=ugettext_lazy('Value'), required=True)

    def __init__(self, tale=None, *args, **kwargs):
        super(TalePreconditionAddForm, self).__init__(*args, **kwargs)
        self.tale = tale
        if not tale is None:
            self.fields['tale_variable'].queryset = TaleVariable.objects.filter(tale=tale)

    def clean_value(self):
        value = self.cleaned_data.get("value")
        if value:
            try:
                int(value)
            except ValueError:
                raise forms.ValidationError(_("Value should be an integer."))
            if int(value) > 2147483646 or int(value) < -2147483646:
                raise forms.ValidationError(_("Value is invalid."))
        return value


@parsleyfy
class TaleConsequenceAddForm(forms.Form):
    CONSEQUENCE_CHOICES = TaleLinkConsequence.CONSEQUENCE_CHOICES

    tale_variable = forms.ModelChoiceField(label=ugettext_lazy('Variable'), queryset=TalePart.objects.all(), required=True)

    consequence = forms.ChoiceField(label=ugettext_lazy('Consequence'), choices=CONSEQUENCE_CHOICES,
                                    initial=CONSEQUENCE_CHOICES[0][0],
                                    required=True)

    value = forms.IntegerField(label=ugettext_lazy('Value'), required=True)

    def __init__(self, tale=None, *args, **kwargs):
        super(TaleConsequenceAddForm, self).__init__(*args, **kwargs)
        self.tale = tale
        if not tale is None:
            self.fields['tale_variable'].queryset = TaleVariable.objects.filter(tale=tale)

    def clean_value(self):
        value = self.cleaned_data.get("value")
        if value:
            try:
                int(value)
            except ValueError:
                raise forms.ValidationError(_("Value should be an integer."))
            if int(value) > 2147483646 or int(value) < -2147483646:
                raise forms.ValidationError(_("Value is invalid."))
        return value


@parsleyfy
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
            raise forms.ValidationError(_("There is another tale part with the same name."))
        return name


@parsleyfy
class TaleAddForm(forms.Form):
    name = forms.CharField(label=ugettext_lazy('Tale Name'),
                           validators=[
                               validators.MinLengthValidator(3),
                               validators.MaxLengthValidator(200)
                           ],
                           help_text=ugettext_lazy(
                               'Give a unique name to your tale. For example: Little Red Riding Hood.'))
    language = forms.ModelChoiceField(label=ugettext_lazy('Language'), queryset=Language.objects.all(), required=True,
                                      help_text=ugettext_lazy(
                                          'Select the language of the tale for categorization purposes.'))
    is_poll_tale = forms.BooleanField(label=ugettext_lazy('Is poll tale?'), initial=False, required=False,
                                      help_text=ugettext_lazy(
                                          'Poll tales advance at designated times according to community votes.'
                                                  'Non-poll tales are individual and unique for every reader.'))

    def clean_name(self):
        name = self.cleaned_data.get("name")
        slug = slugify(name)
        if name and Tale.objects.filter(Q(name=name) | Q(slug=slug)).count() > 0:
            raise forms.ValidationError(_("There is another tale with the same name."))
        return name


@parsleyfy
class TaleLinkAddForm(forms.Form):
    name = forms.CharField(label=ugettext_lazy('Name'),
                             validators=[
                                 validators.MinLengthValidator(3),
                                 validators.MaxLengthValidator(200)
                             ],
                             help_text=ugettext_lazy(
                                 'Link name will not be shown to the readers. It is a unique name for the link'
                                 'to conveniently distinguish it from the other links.'))
    action = forms.CharField(label=ugettext_lazy('Action Text'),
                             validators=[
                                 validators.MinLengthValidator(3),
                                 validators.MaxLengthValidator(200)
                             ],
                             help_text=ugettext_lazy(
                                 'Action text will be shown to the reader to let them select as their choice.'
                                         'According to selected actions, story will advance'))
    source = forms.ModelChoiceField(label=ugettext_lazy('Source'), queryset=TalePart.objects.all(), required=True,
                                    help_text=ugettext_lazy('When this action is selected, the story will depart '
                                                'from the source part.'))
    destination = forms.ModelChoiceField(label=ugettext_lazy('Destination'), queryset=TalePart.objects.all(),
                                         required=True,
                                         help_text=ugettext_lazy('When this action is selected, the story will arrive '
                                                     'to the destination part.'))

    def __init__(self, tale=None, *args, **kwargs):
        super(TaleLinkAddForm, self).__init__(*args, **kwargs)
        self.tale = tale
        if not tale is None:
            self.fields['source'].queryset = TalePart.objects.filter(tale=tale)
            self.fields['destination'].queryset = TalePart.objects.filter(tale=tale)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and TaleLink.objects.filter(name=name, tale=self.tale).count() > 0:
            raise forms.ValidationError(_("There is another link with the same name."))
        return name

    def clean_destination(self):
        source = self.cleaned_data.get("source")
        destination = self.cleaned_data.get("destination")
        if source == destination:
            raise forms.ValidationError(_("Destination cannot be the same as source."))
        return destination


@parsleyfy
class TaleLinkEditForm(TaleLinkAddForm):
    def __init__(self, tale=None, tale_link_name=None, tale_link=None, *args, **kwargs):
        super(TaleLinkEditForm, self).__init__(tale, *args, **kwargs)
        self.tale_link_name = tale_link_name
        if not tale_link is None:
            self.fields['source'].initial = tale_link.source.id
            self.fields['destination'].initial = tale_link.destination.id
            self.fields['action'].initial = tale_link.action
            self.fields['name'].initial = tale_link.name

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and name != self.tale_link_name and TaleLink.objects.filter(name=name,
                                                                                  tale=self.tale).count() > 0:
            raise forms.ValidationError(_("There is another link with the same name."))
        return name