# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.CharField(max_length=512)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('url', models.URLField(max_length=1024, null=True, blank=True)),
                ('ip', models.IPAddressField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('censored', models.BooleanField(default=False)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('description', models.TextField(null=True, blank=True)),
                ('public', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('rendered', models.TextField(null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='ImageEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'image')),
                ('title', models.CharField(max_length=1024)),
                ('caption', models.CharField(max_length=1024, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('description', models.TextField(null=True, blank=True)),
                ('started', models.DateField()),
                ('ended', models.DateField(null=True, blank=True)),
                ('public', models.BooleanField(default=False)),
                ('url', models.URLField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-started'],
            },
        ),
        migrations.CreateModel(
            name='JobGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('jobs', models.ManyToManyField(to='publish.Job', blank=True)),
            ],
            options={
                'ordering': ['-jobs__started'],
            },
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('url', models.URLField(max_length=1024)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=512)),
                ('tagline', models.CharField(max_length=1024, null=True, blank=True)),
                ('slug', models.SlugField()),
                ('public', models.BooleanField(default=False)),
                ('template', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.TextField(null=True, blank=True)),
                ('content', models.TextField()),
                ('issued', models.DateTimeField(null=True, blank=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('publish', models.BooleanField(default=False)),
                ('comments_open', models.BooleanField(default=False)),
                ('source_guid', models.CharField(max_length=1024, null=True, editable=False, blank=True)),
                ('source_date', models.DateTimeField(null=True, editable=False, blank=True)),
                ('source_url', models.URLField(max_length=1024, null=True, editable=False, blank=True)),
                ('log', models.ForeignKey(to='publish.Log')),
            ],
            options={
                'ordering': ['-issued'],
                'verbose_name_plural': 'log entries',
            },
        ),
        migrations.CreateModel(
            name='LogEntryPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.IntegerField(default=0)),
                ('log_entry', models.ForeignKey(to='publish.LogEntry')),
            ],
        ),
        migrations.CreateModel(
            name='LogFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feed', models.URLField(max_length=2048)),
                ('title', models.CharField(max_length=512)),
                ('checked', models.DateTimeField(null=True, blank=True)),
                ('failed', models.DateTimeField(null=True, blank=True)),
                ('log', models.ForeignKey(to='publish.Log')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'photo')),
                ('title', models.CharField(max_length=1024)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('started', models.DateField()),
                ('ended', models.DateField(null=True, blank=True)),
                ('public', models.BooleanField(default=False)),
                ('portfolio', models.BooleanField(default=False)),
                ('url', models.URLField(null=True, blank=True)),
                ('logo', models.ForeignKey(related_name='logos', blank=True, to='publish.Photo', null=True)),
                ('photos', models.ManyToManyField(to='publish.Photo', blank=True)),
            ],
            options={
                'ordering': ['-ended', '-started'],
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=2048)),
                ('authors', models.TextField(null=True, blank=True)),
                ('venue', models.TextField(null=True, blank=True)),
                ('source_url', models.URLField(max_length=2048, null=True, blank=True)),
                ('document', models.FileField(null=True, upload_to=b'publication', blank=True)),
                ('publication_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-publication_date'],
            },
        ),
        migrations.AddField(
            model_name='logentryphoto',
            name='photo',
            field=models.ForeignKey(to='publish.Photo'),
        ),
        migrations.AddField(
            model_name='logentry',
            name='photos',
            field=models.ManyToManyField(to='publish.Photo', through='publish.LogEntryPhoto', blank=True),
        ),
    ]
