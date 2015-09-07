"""https://docs.djangoproject.com/en/1.8/ref/settings/"""

import os

SITE_ID = 1

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'static'), )
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# The maximum length of file paths in file fields
FILE_FIELD_MAX_LENGTH = 1000

AUTH_PROFILE_MODULE = "front.UserProfile"

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'publish',
    'front',
    'staff',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'trullo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'trullo/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.core.context_processors.media',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'trullo.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'trullo.wsgi.application'

TIME_ZONE = 'America/Vancouver'

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

from local_settings import *
