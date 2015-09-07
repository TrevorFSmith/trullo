import datetime
import calendar
import traceback

from django.db.models import Q
from django.contrib import auth
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import feedgenerator
from django.utils.html import strip_tags
from django.template import RequestContext
from django.contrib.auth.models import User
from django.template import Context, loader
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import django.contrib.contenttypes.models as content_type_models
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponsePermanentRedirect

from publish.models import Project, LogEntry, Link
from publish.forms import LinkForm

def index(request):
	context = {
		'recent_log_entries': LogEntry.objects.public_entries(originals=True),
		'recent_log_entry_links': LogEntry.objects.public_entries(originals=False),
	}
	return render_to_response('front/index.html', context, context_instance=RequestContext(request))

def contact(request):
	context = {
		'contact_info': settings.CONTACT_INFO
	}
	return render_to_response('front/contact.html', context, context_instance=RequestContext(request))

def jobs(request):
	context = {}
	if hasattr(settings, 'JOBS_PAGE_CONTACT_INFO'):
		context['contactInfo'] = settings.JOBS_PAGE_CONTACT_INFO
	return render_to_response('front/jobs.html', context, context_instance=RequestContext(request))

@login_required
def link_popup(request):
	if request.method == 'POST':
		link_form = LinkForm(request.POST)
		if link_form.is_valid():
			link_form.save()
			return render_to_response('front/link_popup_close.html', {  }, context_instance=RequestContext(request))
	else:
		link_form = LinkForm(request.GET)
	return render_to_response('front/link_popup.html', { 'link_form':link_form }, context_instance=RequestContext(request))

def item_cmp(item1, item2):
	if item1.__class__ == LogEntry:
		date1 = item1.issued
	elif item1.__class__ == Link:
		date1 = item1.created
	if item2.__class__ == LogEntry:
		date2 = item2.issued
	elif item2.__class__ == Link:
		date2 = item2.created
	if date1 < date2: return 1
	if date1 > date2: return -1
	return 0

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
