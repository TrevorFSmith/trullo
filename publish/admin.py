from django.contrib import admin
from django import forms
from django.forms.utils import ErrorList

from models import *

class StyledAdmin(admin.ModelAdmin):
	class Media:
		css = { "all": ('front/css/admin.css', )}

class CommentAdmin(StyledAdmin):
	list_display = ('author', 'created', 'censored')
admin.site.register(Comment, CommentAdmin)

class ProjectAdmin(StyledAdmin):
	list_display = ('title', 'started', 'ended', 'public', 'portfolio')
admin.site.register(Project, ProjectAdmin)

class JobAdmin(StyledAdmin):
	list_display = ('title', 'started', 'ended', 'public')
admin.site.register(Job, JobAdmin)

class JobGroupAdmin(StyledAdmin):
	list_display = ('title',)
admin.site.register(JobGroup, JobGroupAdmin)

class IdeaAdmin(StyledAdmin):
	list_display = ('title', 'created')
	search_fields = ('title', 'description')
admin.site.register(Idea, IdeaAdmin)

class PhotoAdmin(StyledAdmin):
	pass
admin.site.register(Photo, PhotoAdmin)

class PublicationAdmin(StyledAdmin):
	list_display = ('title', 'venue', 'publication_date')
admin.site.register(Publication, PublicationAdmin)

class LogAdmin(StyledAdmin):
	pass
admin.site.register(Log, LogAdmin)

class LogEntryPhotoInline(admin.TabularInline):
	raw_id_fields = ('photo', )
	model = LogEntryPhoto
	extra = 2

class LogEntryAdmin(StyledAdmin):
	list_display = ('__unicode__', 'log', 'created', 'publish')
	list_filter = ('log', 'publish')
	inlines = (LogEntryPhotoInline,)
	date_hierarchy = 'created'
	search_fields = ('subject', 'content')
admin.site.register(LogEntry, LogEntryAdmin)

class LogEntryPhotoAdmin(StyledAdmin):
	pass
admin.site.register(LogEntryPhoto, LogEntryPhotoAdmin)

class LogFeedAdmin(StyledAdmin):
	pass
admin.site.register(LogFeed, LogFeedAdmin)

class LinkAdmin(StyledAdmin):
	pass
admin.site.register(Link, LinkAdmin)

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
