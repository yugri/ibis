# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 11:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0007_searchquery_email_links'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ibis_site_id', models.CharField(max_length=20)),
                ('site', models.CharField(max_length=20)),
            ],
        ),
    ]
