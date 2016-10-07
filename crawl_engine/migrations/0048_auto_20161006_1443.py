# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-06 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0047_auto_20161005_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchquery',
            name='source',
            field=models.CharField(choices=[('google', 'Google'), ('google_cse', 'Google CSE')], default='google', max_length=15),
        ),
    ]