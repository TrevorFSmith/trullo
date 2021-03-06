from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

def site(request):
	"""Adds site wide context variable"""
	default_collection_log_id = None
	if hasattr(settings, 'DEFAULT_COLLECTION_LOG_ID'):
		default_collection_log_id = settings.DEFAULT_COLLECTION_LOG_ID

	if 'OWNER_USERNAME' in dir(settings):
		owner = User.objects.get(username=settings.OWNER_USERNAME)
	else:
		owner = None

	return {
		'site': Site.objects.get_current(),
		'default_collection_log_id': default_collection_log_id,
		'now': datetime.now(),
		'production': settings.PRODUCTION,
		'author_name': settings.AUTHOR_NAME,
		'owner': owner
	}

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
