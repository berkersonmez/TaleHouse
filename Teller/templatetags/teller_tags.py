from django import template
from Teller.models import Profile
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

register = template.Library()


def get_profile_from_user(value):
    """
    @type value: User
    """
    return Profile.objects.get(user=value)


@register.filter()
def print_follow_button(profile, target):
    if profile.user.username == target.user.username:
        return ''
    if profile.is_following(target):
        return '<a class="btn btn-success btn-xs" href="%s">%s</a>' % (
            reverse('user_follow', args=[target.user.username]),
            _('Unfollow')
        )
    else:
        return '<a class="btn btn-success btn-xs" href="%s">%s</a>' % (
            reverse('user_follow', args=[target.user.username]),
            _('Follow')
        )
