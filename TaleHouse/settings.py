"""
Django settings for TaleHouse project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '59h#sqy8(yd5iw+#opf4cz0@+%8cv7l@rz^2*%zbw-pvc9r3&5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


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
    'bootstrap3_datetime',
    'Teller',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

ROOT_URLCONF = 'TaleHouse.urls'

WSGI_APPLICATION = 'TaleHouse.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'berkerso_talehouse',
        'USER': 'root',
        'PASSWORD': '5x65C46b$7345yBKaL',
        'HOST': ''
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATICFILES_DIRS = (
)

STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_ROOT = os.path.join(BASE_DIR, "upload")

MEDIA_URL = "/upload/"

CKEDITOR_UPLOAD_PATH = "ckeditor/"

CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'admin': {
        'toolbar': 'Full',
    },
    'default': {
        'toolbar': [
            ['Undo', 'Redo',
             '-', 'Bold', 'Italic', 'Underline', 'Format',
             '-', 'SpellChecker', 'Scayt',
             '-', 'Maximize',
            ],
            ['Image',
            ],
            ['HorizontalRule',
             '-', 'BulletedList', 'NumberedList',
             '-', 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord',
             '-', 'SpecialChar',
             '-', 'About',
            ]
        ],
        'width': '100%',
        'font_names': '"Source Sans Pro","Helvetica Neue",Helvetica,Arial,sans-serif',
        'contentsCss': STATIC_URL + 'bootstrap-lumen/css/bootstrap.ckeditor.css'
    },
}

CKEDITOR_RESTRICT_BY_USER = True