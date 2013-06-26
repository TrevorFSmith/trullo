import os
import re
import time
import Image
import urllib
import random
import logging
import calendar
import traceback
import feedparser
import unicodedata
from re import sub
from datetime import datetime, timedelta, date

from django.db import models
from django.conf import settings
from django.db.models import signals
from django.core.mail import send_mail
from django.dispatch import dispatcher
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.html import strip_tags,  linebreaks, urlize
from django.contrib.markup.templatetags.markup import markdown
from django.utils.encoding import force_unicode, smart_unicode, smart_str

#from publish.templatetags.texttags import sanitize_html

class ThumbnailedModel(models.Model):
	"""An abstract base class for models with an ImageField named "image" """
	def thumb(self):
		if not self.image: return ""
		import trullo.publish.templatetags.imagetags as imagetags
		import trullo.imaging as imaging
		try:
			file = settings.MEDIA_URL + self.image.path[len(settings.MEDIA_ROOT):]
			filename, miniature_filename, miniature_dir, miniature_url = imagetags.determine_resized_image_paths(file, "admin_thumb")
			if not os.path.exists(miniature_dir): os.makedirs(miniature_dir)
			if not os.path.exists(miniature_filename): imaging.fit_crop(filename, 100, 100, miniature_filename)
			return """<img src="%s" /></a>""" % miniature_url
		except:
			traceback.print_exc()
			return None
	thumb.allow_tags = True
	class Meta:
		abstract = True

class Photo(ThumbnailedModel):
	image = models.ImageField(upload_to='photo', blank=False)
	title = models.CharField(max_length=1024, null=False, blank=False)
	created = models.DateTimeField(auto_now_add=True)
	@models.permalink
	def get_absolute_url(self):
		return ('publish.views.photo', (), { 'id':self.id })
	class Meta:
		ordering = ['-created']
	def __unicode__(self):
		if self.title: return self.title
		return self.image

class Publication(models.Model):
	"""A record of papers which have been published in journals or conferences."""
	title = models.CharField(max_length=2048, blank=False, null=False)
	authors = models.TextField(blank=True, null=True)
	venue = models.TextField(blank=True, null=True)
	source_url = models.URLField(blank=True, null=True, max_length=2048, editable=True)
	document = models.FileField(upload_to='publication', blank=True, null=True)
	publication_date = models.DateTimeField(null=True, blank=True)

	def __unicode__(self): return self.title

	class Meta:
		ordering = ['-publication_date']

class Idea(models.Model):
	"""A concept or thought for an action or project."""
	title = models.CharField(max_length=1024, blank=False, null=False)
	description = models.TextField(blank=True, null=True)
	public = models.BooleanField(default=False, blank=False, null=False)
	created = models.DateTimeField(null=False, blank=False, default=datetime.now)
	rendered = models.TextField(blank=True, null=True, editable=False)

	def save(self, *args, **kwargs):
		"""When saving the content, render via markdown and save to self.rendered"""
		self.rendered = markdown(urlize(self.description))
		super(Idea, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.title
	class Meta:
		ordering = ['-created']

class Project(models.Model):
	"""A work or personal project description."""
	title = models.CharField(max_length=1024, blank=False, null=False)
	slug = models.SlugField(blank=False, null=False, unique=True)
	description = models.TextField(blank=True, null=True)
	started = models.DateField(blank=False, null=False)
	ended = models.DateField(blank=True, null=True)
	public = models.BooleanField(default=False, blank=False, null=False)
	portfolio = models.BooleanField(default=False, blank=False, null=False)
	photos = models.ManyToManyField(Photo, blank=True, null=True)
	url = models.URLField(null=True, blank=True)
	logo = models.ForeignKey(Photo, blank=True, null=True, related_name='logos')

	def __unicode__(self): return self.title
	class Meta:
		ordering = ['-started', '-ended']

class Comment(models.Model):
	author = models.CharField(max_length=512, blank=False, null=False)
	email = models.EmailField(blank=True, null=True)
	url = models.URLField(blank=True, null=True, max_length=1024)
	ip = models.IPAddressField(blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True)
	comment = models.TextField(blank=False, null=False)
	censored = models.BooleanField(blank=False, null=False, default=False)
	
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	def __unicode__(self):
		return self.author
	class Meta:
		ordering = ['-created']

class Log(models.Model):
	"""Some would call it a [we]blog, but this is a web app so let's assume that it's on the web, ok?"""
	title = models.CharField(max_length=512, blank=False, null=False)
	tagline = models.CharField(max_length=1024, blank=True, null=True)
	slug = models.SlugField()
	public = models.BooleanField(default=False, blank=False, null=False)
	template = models.CharField(max_length=120, blank=False, null=False)
	def published_entries(self):
		return LogEntry.objects.filter(log=self, publish=True)
	@models.permalink
	def get_feed_url(self):
		return ('publish.views.log_feed', (), { 'slug':self.slug })
	@models.permalink
	def get_absolute_url(self):
		return ('publish.views.log', (), { 'slug':self.slug })
	def __unicode__(self):
		return self.title

class LogEntryPhoto(models.Model):
	log_entry = models.ForeignKey('LogEntry', blank=False, null=False)
	photo = models.ForeignKey('Photo', blank=False, null=False)
	weight = models.IntegerField(default=0, blank=False, null=False)

class LogEntryManager(models.Manager):
	def public_entries(self):
		return self.filter(publish=True, log__public=True)

class LogEntry(models.Model):
	log = models.ForeignKey(Log, blank=False, null=False)
	subject = models.TextField(blank=True, null=True)
	content = models.TextField(blank=False, null=False)
	issued = models.DateTimeField(blank=True, null=True)
	modified = models.DateTimeField(auto_now=True, blank=False, null=False)
	created = models.DateTimeField(auto_now_add=True)
	publish = models.BooleanField(blank=False, null=False, default=False)
	comments = generic.GenericRelation(Comment)
	comments_open = models.BooleanField(blank=False, null=False, default=False)
	photos = models.ManyToManyField(Photo, blank=True, null=True, through='LogEntryPhoto')

	# for entries which are imported from remote streams, these fields store source info
	source_guid = models.CharField(max_length=1024, blank=True, null=True, editable=False)
	source_date = models.DateTimeField(blank=True, null=True, editable=False)
	source_url = models.URLField(blank=True, null=True, max_length=1024, editable=False)

	objects = LogEntryManager()
	
	def summary(self): # returns a dictionary: {title, content, date, url} for use in mixed lists
		return {'title':self.subject, 'content':self.content, 'date':self.issued, 'url':self.get_absolute_url(), 'type':'logentry' }
	def __unicode__(self):
		if self.subject: return self.subject
		return 'No Subject'
	def get_absolute_url(self):
		if self.source_url: return str(self.source_url)
		return reverse('publish.views.log_entry', args=[], kwargs={ 'slug':self.log.slug, 'pk':self.id })
	class Meta:
		verbose_name_plural = "log entries"
		ordering = ['-issued']

def convert_to_ascii(value):
	return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')

def remove_linebreak_tags(value):
	if value == None: return None
	value = sub('<p[^>]*>', '', value)
	value = sub('<br[^>]*>', '', value)
	return sub('</p[^>]*>', '', value)

class LogFeed(models.Model):
	"""An RSS or Atom feed used to create log entries."""
	log = models.ForeignKey(Log, blank=False, null=False)
	feed = models.URLField(blank=False, null=False, max_length=2048)
	title = models.CharField(max_length=512, blank=False, null=False)
	checked = models.DateTimeField(blank=True, null=True)
	failed = models.DateTimeField(blank=True, null=True)
	def check_feed(self):
		"""Fetch the feed and create log entries for each item."""
		logging.info("checking log feed: %s" % self.feed)
		doc = feedparser.parse(self.feed)
		for entry in doc.entries:
			log_entry = LogEntry(log=self.log)
			log_entry.subject = convert_to_ascii(sanitize_html(entry.title))

			if entry.has_key('content'): log_entry.content = entry.content[0].value
			elif entry.has_key('summary'): log_entry.content = entry.summary
			elif entry.has_key('subtitle'): log_entry.content = entry.subtitle
			if log_entry.content: log_entry.content = convert_to_ascii(sanitize_html(log_entry.content))

			log_entry.source_guid = entry.id
			log_entry.source_url = entry.link

			log_entry.issued = datetime.now()
			if entry.has_key('published_parsed'): log_entry.source_date = datetime(*entry.published_parsed[:6])
			if log_entry.source_date: log_entry.issued = log_entry.source_date
			
			# check that we haven't already recorded this entry
			if LogEntry.objects.filter(source_guid=log_entry.source_guid).count() > 0: continue
			if LogEntry.objects.filter(source_url=log_entry.source_url).count() > 0: continue
			log_entry.publish = True
			log_entry.save()
		logging.info("completed log feed check")
	def __unicode__(self):
		return self.title

class LinkManager(models.Manager):
	def public_entries(self):
		return self.filter(public=True)

class Link(models.Model):
	name = models.CharField(max_length=1024, blank=False)
	url = models.URLField(blank=False, null=False, max_length=1024)
	description = models.TextField(blank=True)
	created = models.DateTimeField(auto_now_add=True)
	public = models.BooleanField(default=True, blank=False, null=False)
	
	objects = LinkManager()
	
	def summary(self): # returns a dictionary: {title, content, date, url, type} for use in mixed lists
		return {'title':self.name, 'content':self.description, 'date':self.created, 'url':self.get_absolute_url(), 'type':'link' }
	def get_absolute_url(self):
		return self.url
	def __unicode__(self):
		return self.name
	class Meta:
		ordering = ['-created']

class ImageEntry(models.Model):
	image = models.ImageField(upload_to='image', blank=False)
	title = models.CharField(max_length=1024, null=False, blank=False)
	caption = models.CharField(max_length=1024, null=True, blank=True)
	description = models.TextField(blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True)
	@models.permalink
	def get_absolute_url(self):
		return (views.image, (), { 'id':self.id })
	class Meta:
		ordering = ['-created']
	def __unicode__(self):
		return self.image


# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
