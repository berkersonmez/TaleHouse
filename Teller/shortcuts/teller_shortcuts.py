from django.shortcuts import render
from django.http import HttpRequest
from Teller.models import Profile
from Teller.forms import UserLoginForm


def render_with_defaults(request, template_name, context):
    """
    @type request: HttpRequest
    @type context: Dict
    """
    if request.user.is_authenticated():
        profile = Profile.objects.get(user__username=request.user.username)
        context.update({'profile': profile})
    else:
        form = UserLoginForm()
        context.update({'user_login_form': form})
    return render(request, template_name, context)