# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-15 08:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0010_auto_20170415_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchquery',
            name='response_address',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]