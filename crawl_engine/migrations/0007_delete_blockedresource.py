# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-23 11:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0006_blockedresource'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BlockedResource',
        ),
    ]
