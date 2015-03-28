"""
Django settings for TaleHouse project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'ckeditor',
    'widget_tweaks',
    'bootstrap3',
    'bootstrap3_datetime',
    'captcha',
    'parsley',
    'social.apps.django_app.default',
    'Teller',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "social.apps.django_app.context_processors.backends",
    "social.apps.django_app.context_processors.login_redirect",
)

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.Facebook2OAuth2',
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'TaleHouse.urls'

WSGI_APPLICATION = 'TaleHouse.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('tr', _('Turkish')),
    ('en', _('English')),
)

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SOUTH_MIGRATION_MODULES = {
    'captcha': 'captcha.south_migrations',
    'default': 'social.apps.django_app.default.south_migrations'
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "Teller/static"),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# MEDIA_ROOT = os.path.join(BASE_DIR, "upload")

# MEDIA_URL = "/upload/"

CKEDITOR_UPLOAD_PATH = "ckeditor/"

CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'admin': {
        'toolbar': 'Full',
    },
    'default': {
        'toolbar': [
            ['Undo', 'Redo',
             '-', 'Bold', 'Italic', 'Underline', 'Format'
             ],
            ['HorizontalRule',
             '-', 'BulletedList', 'NumberedList',
             '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight',
             ],
            ['Image'
             ],
            ['TaleLogic', 'TaleLogicInline', 'TaleLogicVariable'
             ],
            ['Maximize']
        ],
        'skin': 'bootstrapck',
        'width': '100%',
        'font_names': '"Source Sans Pro","Helvetica Neue",Helvetica,Arial,sans-serif',
        'contentsCss': STATIC_URL + 'bootstrap-lumen/css/bootstrap.ckeditor.css',
        'extraPlugins': 'lineutils,clipboard,widget,talelogic',
        'format_tags': 'p;h2;h3',
        'removeDialogTabs': 'link:upload;image:Upload',
        'filebrowserBrowseUrl': '',
        'filebrowserImageBrowseUrl': '',
        'filebrowserFlashBrowseUrl': ''
    },
}

CKEDITOR_RESTRICT_BY_USER = True

CAPTCHA_FOREGROUND_COLOR = '#158cba'

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_LOGIN_ERROR_URL = '/'

TELLER_MAX_LINKS_PER_PART = 10
TELLER_MAX_PARTS_PER_TALE = 50
TELLER_MAX_TALES_PER_USER = 15
TELLER_MAX_VARIABLES_PER_TALE = 20

TELLER_CONTENT_SAFE_ATTRS = frozenset([
    'abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align',
    'alt', 'axis', 'border', 'cellpadding', 'cellspacing', 'char', 'charoff',
    'charset', 'checked', 'cite', 'class', 'clear', 'cols', 'colspan',
    'color', 'compact', 'coords', 'datetime', 'dir', 'disabled', 'enctype',
    'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace', 'id',
    'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method',
    'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly',
    'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape',
    'size', 'span', 'src', 'start', 'summary', 'tabindex', 'target', 'title',
    'type', 'usemap', 'valign', 'value', 'vspace', 'width', 'data-talelogic',
    'data-talelogic-variable'])