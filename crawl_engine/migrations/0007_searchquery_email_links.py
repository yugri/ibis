# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 08:43
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0006_blockedresource'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchquery',
            name='email_links',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
