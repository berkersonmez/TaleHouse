from django import template
from Teller.models import Profile, Rating
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
            reverse('user_follow', args=[target.slug]),
            _('Unfollow')
        )
    else:
        return '<a class="btn btn-success btn-xs" href="%s">%s</a>' % (
            reverse('user_follow', args=[target.slug]),
            _('Follow')
        )


@register.filter()
def print_rate_buttons(profile, tale):
    if profile == tale.user:
        return ''
    rating = Rating.objects.filter(tale=tale, user=profile)
    if rating.count() > 0:
        return '<p>You have rated this tale %d out of 5</p>' % rating[0].rating
    return """<p>Rate this tale:</p>
            <div class="btn-group">
                  <a href="%s" class="btn btn-default">1</a>
                  <a href="%s" class="btn btn-default">2</a>
                  <a href="%s" class="btn btn-default">3</a>
                  <a href="%s" class="btn btn-default">4</a>
                  <a href="%s" class="btn btn-default">5</a>
            </div>""" % (
        reverse('tale_rate', args=[tale.id, 1]),
        reverse('tale_rate', args=[tale.id, 2]),
        reverse('tale_rate', args=[tale.id, 3]),
        reverse('tale_rate', args=[tale.id, 4]),
        reverse('tale_rate', args=[tale.id, 5])
    )