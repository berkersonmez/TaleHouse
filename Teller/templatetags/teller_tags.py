from django import template
from django.templatetags.static import static
from django.utils.http import urlencode
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
        return '<p>' + _('You have rated this tale %(rating)s out of 5') % {'rating': rating[0].rating} + '</p>'
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

@register.filter()
def print_tale_share_buttons(link, tale):
    return """
    <a onclick="return !window.open(this.href, 'Share on Facebook', 'width=640, height=536')" href="%s" target="_window" class="btn btn-facebook btn-logoandtext"><img src="%s"> %s</a>
    <a onclick="return !window.open(this.href, 'Share on Twitter', 'width=640, height=536')" href="%s" class="btn btn-twitter btn-logoandtext"><img src="%s"> %s</a>
    <a onclick="return !window.open(this.href, 'Share on Google+', 'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600')" href="%s" class="btn btn-google btn-logoandtext"><img src="%s"> %s</a>

    """ % (
        "https://www.facebook.com/sharer/sharer.php?u=href=" + link + "&display=popup&ref=plugin", static("Teller/img/fb-logo.png"), _("Share"),
        "https://twitter.com/share?url=" + link + "&text=" + tale.name + "&hashtags=interactale", static('Teller/img/twitter-bird-logo.png'), _('Tweet'),
        "https://plus.google.com/share?url=" + link + "", static('Teller/img/google-logo.png'), _('Share'),
    )
