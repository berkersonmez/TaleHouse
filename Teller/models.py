from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from decimal import *


class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('user'))
    selected_links = models.ManyToManyField('TaleLink', verbose_name=_('selected links'), blank=True, null=True)
    followed_users = models.ManyToManyField('self', verbose_name=_('followed users'), blank=True, null=True,
                                            symmetrical=False)

    def __unicode__(self):
        return u"%s" % self.user.username

    def is_following(self, target):
        return target in self.followed_users.all()


class Tale(models.Model):
    user = models.ForeignKey(Profile, verbose_name=_('user'), related_name='tales')
    name = models.CharField(_('name'), max_length=200)
    created_at = models.DateTimeField(_('creation date'), auto_now_add=True)
    language = models.ForeignKey('Language', verbose_name=_('language'))
    is_poll_tale = models.BooleanField(_('is poll tale'), default=False)
    is_published = models.BooleanField(_('is published'), default=False)
    slug = models.SlugField(_('slug'), max_length=150, unique=True)
    overall_rating = models.DecimalField(_('rating'), max_digits=3, decimal_places=2, default=Decimal(0))

    def __unicode__(self):
        return u"%s" % self.name


class TalePart(models.Model):
    tale = models.ForeignKey(Tale, verbose_name=_('tale'))
    name = models.CharField(_('name'), max_length=200)
    content = RichTextField(_('content'))
    created_at = models.DateTimeField(_('creation date'), auto_now_add=True)
    is_active = models.BooleanField(_('is active'), default=True)
    is_start = models.BooleanField(_('is start part'), default=False)
    poll_end_date = models.DateTimeField(_('vote end date'), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.name


class TaleLink(models.Model):
    source = models.ForeignKey(TalePart, verbose_name=_('source tale part'), related_name='choices')
    destination = models.ForeignKey(TalePart, verbose_name=_('destination tale part'), blank=True, null=True,
                                    related_name='entrances')
    action = models.CharField(_('action'), max_length=200)
    tale = models.ForeignKey(Tale, verbose_name=_('tale'))

    def __unicode__(self):
        return u"%s" % self.action


class Language(models.Model):
    name = models.CharField(_('language name'), max_length=20)
    code = models.SlugField(_('code'), max_length=4, unique=True)

    def __unicode__(self):
        return u"%s" % self.name


class Rating(models.Model):
    user = models.ForeignKey(Profile, verbose_name=_('user'), related_name='ratings')
    tale = models.ForeignKey(Tale, verbose_name=_('tale'), related_name='ratings')
    rating = models.DecimalField(_('rating'), decimal_places=1, max_digits=2, default=Decimal(0))

    def __unicode__(self):
        return u"%d" % self.rating