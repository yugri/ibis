# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-31 12:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0033_auto_20160826_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='top_image_url',
            field=models.URLField(blank=True, max_length=1000),
        ),
    ]