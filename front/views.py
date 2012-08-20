import datetime
import calendar
import pprint
import traceback

from django.conf import settings
from django.db.models import Q
from django.template import Context, loader
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
import django.contrib.contenttypes.models as content_type_models
from django.template import RequestContext
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.utils import feedgenerator

from trullo.front.models import *
from trullo.publish.models import *
from trullo.publish.forms import *

def index(request):
	current_projects = Project.objects.filter(public=True, portfolio=True, ended=None)
	previous_projects = Project.objects.filter(public=True, portfolio=True).exclude(ended=None)
	latest = list(LogEntry.objects.public_entries()[:10])
	latest.extend(Link.objects.public_entries()[:10])
	latest.sort(item_cmp)
	return render_to_response('front/index.html', { 'latest':latest, 'current_projects':current_projects, 'previous_projects':previous_projects }, context_instance=RequestContext(request))

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