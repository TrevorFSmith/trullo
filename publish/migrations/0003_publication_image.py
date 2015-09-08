# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publish', '0002_auto_20150908_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='image',
            field=models.ImageField(upload_to=b'publication_image', blank=True),
        ),
    ]
