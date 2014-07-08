from django import template
from Teller.models import Profile
from django.contrib.auth.models import User

register = template.Library()


def get_profile_from_user(value):
    """
    @type value: User
    """
    return Profile.objects.get(user=value)
