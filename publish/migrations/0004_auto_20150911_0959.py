# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publish', '0003_publication_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='publication',
            name='slug',
            field=models.SlugField(null=True, blank=True),
        ),
    ]
