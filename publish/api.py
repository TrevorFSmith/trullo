from tastypie import fields
from tastypie.api import Api
from tastypie.paginator import Paginator
from datetime import datetime, timedelta, date
from tastypie.validation import FormValidation
from tastypie.authentication import Authentication, SessionAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, include, url
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponsePermanentRedirect

from publish.forms import IdeaForm
from publish.models import Project, Idea, Publication, LogEntry, Log, Idea, Job, JobGroup

from trullo import API

class LogResource(ModelResource):
	class Meta:
		queryset = Log.objects.all()
		include_absolute_url = True
		filtering = {
			'slug': ['exact'],
			'public': ['exact'],
		}
	def get_object_list(self, request):
		objects = super(LogResource, self).get_object_list(request)
		if request.user.is_authenticated(): return objects
		return objects.filter(public=True)
API.register(LogResource())

class LogEntryResource(ModelResource):
	log = fields.ForeignKey(LogResource, 'log')
	class Meta:
		queryset = LogEntry.objects.all()
		resource_name = 'log-entry'
		allowed_methods = ['get']
		include_absolute_url = True
		paginator_class = Paginator
		filtering = {
			'log': ALL_WITH_RELATIONS,
			'source_url': ['isnull'],
			'publish':['exact'],
		}
	def get_object_list(self, request):
		objects = super(LogEntryResource, self).get_object_list(request)
		if request.user.is_authenticated(): return objects
		return objects.filter(publish=True, log__public=True)
API.register(LogEntryResource())

class PublicationResource(ModelResource):
	class Meta:
		queryset = Publication.objects.all()
		allowed_methods = ['get']
API.register(PublicationResource())

class ProjectResource(ModelResource):
	class Meta:
		queryset = Project.objects.all()
		allowed_methods = ['get']

	def get_object_list(self, request):
		projects = super(ProjectResource, self).get_object_list(request)
		if request.user.is_authenticated(): return projects
		return projects.filter(public=True)

	def prepend_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
		]
API.register(ProjectResource())

class IdeaResource(ModelResource):
	created = fields.DateTimeField(readonly=True)
	rendered = fields.CharField(readonly=True)

	class Meta:
		queryset = Idea.objects.all()
		allowed_methods = ['get', 'post']
		validation = FormValidation(form_class=IdeaForm)
		authorization = DjangoAuthorization()

	def get_object_list(self, request):
		items = super(IdeaResource, self).get_object_list(request)
		if request.user.is_authenticated(): return items
		return items.filter(public=True)
API.register(IdeaResource())

class JobResource(ModelResource):
	class Meta:
		queryset = Job.objects.all()
		allowed_methods = ['get']
		authorization = DjangoAuthorization()

	def get_object_list(self, request):
		items = super(JobResource, self).get_object_list(request)
		if request.user.is_authenticated(): return items
		return items.filter(public=True)
API.register(JobResource())

class JobGroupResource(ModelResource):
	jobs = fields.ToManyField(JobResource, 'jobs', null=True, full=True)
	class Meta:
		queryset = JobGroup.objects.all()
		allowed_methods = ['get']
		authorization = DjangoAuthorization()
API.register(JobGroupResource())

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
