# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0048_auto_20161006_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='article_url',
            field=models.URLField(db_index=True, max_length=1000),
        ),
    ]