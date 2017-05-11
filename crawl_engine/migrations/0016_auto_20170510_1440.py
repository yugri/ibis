# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0015_delete_duplicate_article_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='article_url',
            field=models.URLField(max_length=2048, unique=True),
        ),
    ]