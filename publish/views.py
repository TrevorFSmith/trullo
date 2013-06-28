import time
import rfc822
import tweepy
import urllib
import calendar
import traceback
from datetime import datetime, timedelta, date

from django.db.models import Q
from django.contrib import auth
from django.conf import settings
from django.core.cache import cache
from django.utils.html import urlize
from django.utils import feedgenerator
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template import RequestContext
from django.contrib.auth.models import User
from django.template import Context, loader
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import django.contrib.contenttypes.models as content_type_models
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.admin.views.decorators import staff_member_required

from forms import CollectForm, LinkForm, IdeaForm, CommentForm
from models import Photo, Publication, Idea, Project, Comment, Log, LogEntry, ImageEntry, LogEntryPhoto, LogFeed, Link

def index(request):
	return render_to_response('publish/index.html', { 'logs':Log.objects.all() }, context_instance=RequestContext(request))

@login_required
def collect(request):
	return render_to_response('publish/collect.html', { }, context_instance=RequestContext(request))

@login_required
def collect_form(request):
	page_message = None
	if request.method == 'GET':
		collect_form = CollectForm(initial=request.GET)
	else:
		collect_form = CollectForm(request.POST)
		if collect_form.is_valid():
			log_entry = LogEntry()
			log_entry.log = collect_form.cleaned_data['log']
			log_entry.subject = collect_form.cleaned_data['title']
			log_entry.content = '<blockquote>%s</blockquote><p class="collection-note">%s</p>' % (collect_form.cleaned_data['excerpt'] or '', collect_form.cleaned_data['note'] or '')
			log_entry.publish = collect_form.cleaned_data['make_public']
			log_entry.source_url = collect_form.cleaned_data['url']
			log_entry.issued = datetime.now()
			log_entry.save()
			page_message = 'The <a href="%s">log entry</a> was created.' % reverse('publish.views.log_entry', args=[], kwargs={'slug':log_entry.log.slug, 'pk':log_entry.id})
	return render_to_response('publish/collect_form.html', { 'collect_form':collect_form, 'page_message':page_message }, context_instance=RequestContext(request))

def publications(request):
	return render_to_response('publish/publications.html', {}, context_instance=RequestContext(request))

def merge(request):
	return render_to_response('publish/merge.html', { }, context_instance=RequestContext(request))

def ideas(request):
	return render_to_response('publish/ideas.html', { 'ideas':Idea.objects.all() }, context_instance=RequestContext(request))
		
def projects(request):
	return render_to_response('publish/projects.html', { 'projects':Project.objects.all() }, context_instance=RequestContext(request))
	
def log(request, slug):
	log = get_object_or_404(Log, slug=slug)
	if not request.user.is_staff and not log.public:
		return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
	return render_to_response('publish/log.html', { 'log':log, 'archive_years':LogEntry.objects.filter(log=log).dates("issued", "year") }, context_instance=RequestContext(request))

def log_archive(request, slug):
	return log_year_archive(request, slug, datetime.now().year)

def log_year_archive(request, slug, year):
	log = get_object_or_404(Log, slug=slug)
	if not request.user.is_staff and not log.public:
		return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
	return render_to_response('publish/log_archive.html', { 'log':log, 'entries':LogEntry.objects.filter(log=log, issued__year=year),'archive_years':LogEntry.objects.filter(log=log).dates("issued", "year") }, context_instance=RequestContext(request))

def log_feed(request, slug):
	log = get_object_or_404(Log, slug=slug)
	if not request.user.is_staff and not log.public:
		return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

	cache_key = "trullo.feed.log.%s" % slug
	cached_feed = cache.get(cache_key)
	if cached_feed: return HttpResponse(cached_feed, mimetype='application/rss+xml')
	
	site = Site.objects.get_current()
	feed = feedgenerator.DefaultFeed(
		title = log.title,
		link = "http://" + site.domain + log.get_absolute_url(),
		feed_url = "http://" + site.domain + log.get_feed_url(),
		description=log.tagline,
		language="en",
	)
	for entry in log.published_entries().all()[:10]: add_log_entry_to_feed(entry, feed)
	cached_feed = feed.writeString('utf-8')
	cache.set(cache_key, cached_feed, 360)
	return HttpResponse(cached_feed, mimetype='application/rss+xml')

def add_log_entry_to_feed(entry, feed):
	if entry.source_url:
		link = entry.get_absolute_url()
	else:
		link = "http://%s%s" % (Site.objects.get_current().domain, entry.get_absolute_url())
	feed.add_item(title=strip_tags(entry.subject), link=link, description=entry.content, pubdate=entry.issued)

def add_story_to_feed(story, feed):
	site = Site.objects.get_current()
	if story.authors.all().count() > 0:
		author_name = story.authors.all()[0].get_profile().display_name
	else:
		author_name = None
	link = "http://" + site.domain + story.get_absolute_url()
	feed.add_item(title=strip_tags(story.headline), link=link, description=story.body, author_name=author_name, pubdate=story.start_date)

def log_entry(request, slug, pk):
	entry = get_object_or_404(LogEntry, log__slug=slug, pk=pk)
	if not request.user.is_staff:
		if not entry.publish: raise Http404
		if not entry.log.public: raise Http404
	
	return render_to_response('publish/log_entry.html', { 'log_entry':entry, 'archive_years':LogEntry.objects.filter(log=entry.log).dates("issued", "year") }, context_instance=RequestContext(request))

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
