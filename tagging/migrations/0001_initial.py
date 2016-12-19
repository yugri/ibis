# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-11 14:36
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='name')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]