from django.conf.urls import patterns

urlpatterns = patterns('',
	(r'^$', 'publish.views.index'),
	(r'^idea/$', 'publish.views.ideas'),
	(r'^post/$', 'publish.views.posts'),
	(r'^publication/$', 'publish.views.publications'),
	(r'^publication/(?P<slug>[^/]+)/$', 'publish.views.publication'),
	(r'^project/$', 'publish.views.projects'),

	(r'^merge/$', 'publish.views.merge'),

	(r'^collect/$', 'publish.views.collect'),
	(r'^collect-form/$', 'publish.views.collect_form'),

	(r'^photo/(?P<id>[^/]+)/$', 'publish.views.photo'),

	(r'^(?P<slug>[^/]+)/$', 'publish.views.log'),
	(r'^(?P<slug>[^/]+)/archive/$', 'publish.views.log_archive'),
	(r'^(?P<slug>[^/]+)/archive/(?P<year>[\d]+)/$', 'publish.views.log_year_archive'),
	(r'^(?P<slug>[^/]+)/feed/$', 'publish.views.log_feed'),
	(r'^(?P<slug>[^/]+)/(?P<pk>[\d]+)/$', 'publish.views.log_entry'),
)

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
