# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-13 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0005_auto_20160713_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='post_date_crawled',
            field=models.DateField(auto_created=True, null=True),
        ),
    ]