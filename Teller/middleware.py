from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render, redirect
from social.exceptions import *
from django.utils.translation import ugettext as _


class TellerSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect('error_info', _('You canceled the authentication'))
        if type(exception) == AuthFailed:
            return redirect('error_info', _('Authentication has failed'))
        if type(exception) == AuthUnknownError:
            return redirect('error_info', _('An unknown error occurred while trying to authenticate'))
        if type(exception) == AuthTokenError:
            return redirect('error_info', _('Permission error occurred while trying to authenticate'))
        if type(exception) == AuthMissingParameter:
            return redirect('error_info', _('Parameter error occurred while trying to authenticate'))
        if type(exception) == AuthAlreadyAssociated:
            return redirect('error_info', _('The account has already been associated with a different user'))
        if type(exception) == WrongBackend:
            return redirect('error_info', _('An error occurred while trying to authenticate'))
        if type(exception) == NotAllowedToDisconnect:
            return redirect('error_info', _('Associate another account to disconnect the account'))
        if type(exception) == AuthStateMissing:
            return redirect('error_info', _('An error occurred while trying to authenticate'))
        if type(exception) == AuthStateForbidden:
            return redirect('error_info', _('An error occurred while trying to authenticate'))
        if type(exception) == AuthTokenRevoked:
            return redirect('error_info', _('An error occurred while trying to authenticate'))
        else:
            pass