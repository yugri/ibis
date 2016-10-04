# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-02 08:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0035_searchquery_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='article_url',
            field=models.URLField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='article',
            name='top_image',
            field=models.ImageField(blank=True, max_length=1000, null=True, upload_to='article-images'),
        ),
    ]