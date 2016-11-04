# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-03 17:29
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0052_auto_20161103_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchquery',
            name='source',
            field=django.contrib.postgres.fields.jsonb.JSONField(choices=[('google', 'Google'), ('google-cse', 'Google CSE'), ('google-blogs', 'Google Blogs'), ('google-news', 'Google News'), ('google-scholar', 'Google Scholar')], default='google'),
        ),
    ]
