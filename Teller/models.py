from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('user'))
    selected_links = models.ManyToManyField('TaleLink', verbose_name=_('selected links'), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.user.username


class Tale(models.Model):
    user = models.ForeignKey(Profile, verbose_name=_('user'), related_name='tales')
    name = models.CharField(_('name'), max_length=200)
    created_at = models.DateTimeField(_('creation date'), auto_now_add=True)
    language = models.ForeignKey('Language', verbose_name=_('language'))
    is_poll_tale = models.BooleanField(_('is poll tale'), default=False)
    slug = models.SlugField(_('slug'), max_length=150, unique=True)

    def __unicode__(self):
        return u"%s" % self.name


class TalePart(models.Model):
    tale = models.ForeignKey(Tale, verbose_name=_('tale'))
    name = models.CharField(_('name'), max_length=200)
    content = RichTextField(_('content'))
    created_at = models.DateTimeField(_('creation date'), auto_now_add=True)
    is_active = models.BooleanField(_('is active'), default=True)
    poll_end_date = models.DateTimeField(_('vote end date'), blank=True, null=True)
    slug = models.SlugField(_('slug'), max_length=150, unique=True)

    def __unicode__(self):
        return u"%s" % self.name


class TaleLink(models.Model):
    source = models.ForeignKey(TalePart, verbose_name=_('source tale part'), related_name='choices')
    destination = models.ForeignKey(TalePart, verbose_name=_('destination tale part'), blank=True, null=True,
                                    related_name='entrances')
    action = models.CharField(_('action'), max_length=200)

    def __unicode__(self):
        return u"%s" % self.action


class Language(models.Model):
    name = models.CharField(_('language name'), max_length=20)
    code = models.SlugField(_('code'), max_length=4, unique=True)

    def __unicode__(self):
        return u"%s" % self.name