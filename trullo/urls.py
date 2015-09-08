from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
	(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.gif', permanent=True)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

	(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'admin/login.html'}),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True)),

	(r'^publish/', include('publish.urls')),
	(r'^', include('front.urls')),
)

if settings.DEBUG:
	urlpatterns += staticfiles_urlpatterns()

	urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
			'document_root': settings.MEDIA_ROOT,
		}),
	)

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
