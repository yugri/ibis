# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-11 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0027_auto_20160811_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='search_id',
            field=models.CharField(blank=True, max_length=124, null=True),
        ),
    ]
