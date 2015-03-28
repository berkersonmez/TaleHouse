from django.shortcuts import render
from django.http import HttpRequest
from social.apps.django_app.default.models import UserSocialAuth
from Teller.models import Profile
from Teller.forms import UserLoginForm


def render_with_defaults(request, template_name, context):
    """
    @type request: HttpRequest
    @type context: Dict
    """
    if request.user.is_authenticated():
        profile = Profile.objects.get(user__username=request.user.username)
        google_associated = UserSocialAuth.objects.filter(user=profile.user, provider='google-oauth2').count() > 0
        facebook_associated = UserSocialAuth.objects.filter(user=profile.user, provider='facebook').count() > 0
        context.update({'profile': profile,
                        'google_associated': google_associated,
                        'facebook_associated': facebook_associated})
    else:
        form = UserLoginForm()
        context.update({'user_login_form': form})
    return render(request, template_name, context)