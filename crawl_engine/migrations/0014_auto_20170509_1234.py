# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-09 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0013_auto_20170425_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrashFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(default='.', max_length=255, verbose_name='Url filter regular expression')),
                ('text', models.CharField(default='.', max_length=255, verbose_name='Text filter regular expression')),
                ('length', models.IntegerField(default=0, verbose_name='Maximum text length for filter to work.')),
            ],
        ),
        migrations.DeleteModel(
            name='BlockedSite',
        ),
    ]