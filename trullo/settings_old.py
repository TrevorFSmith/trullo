import os 

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
BACKUP_ROOT = os.path.join(PROJECT_ROOT, 'backups')
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
TEMPLATE_DIRS = os.path.join(PROJECT_ROOT, 'templates')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATIC_ROOT = '/mnt/static/'

STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'static'), )

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AUTH_PROFILE_MODULE = "front.UserProfile"

SOUTH_AUTO_FREEZE_APP = True

USE_I18N = False

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
	'django.core.context_processors.static',
    'django.core.context_processors.request',
	'trullo.context_processors.site',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'django.contrib.admindocs',
	'tastypie',
	'backbone_tastypie',
	'gunicorn',
	'south',
	'trullo.publish',
	'trullo.front',
	'trullo.staff',
)

# Tasty Pie settings
API_LIMIT_PER_PAGE = 1000

from local_settings import *

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
