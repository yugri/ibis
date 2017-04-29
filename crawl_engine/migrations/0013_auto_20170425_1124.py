# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-25 11:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0012_auto_20170421_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockedsite',
            name='site',
            field=models.CharField(help_text='\n            To block entire domain use <b>example\\.com</b>.\n            To block subdomain use <b>sub\\.example\\.com</b>.\n            To blcok specific files from domain use <b>sub\\.example\\.com.*\\.pdf</b>.\n            You can test expressions in <a href="http://regexr.com/" target="_blank">online tool</a>.\n        ', max_length=255, verbose_name='Block url regexp'),
        ),
    ]