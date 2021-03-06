# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-18 23:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0001_initial'),
        ('crawl_engine', '0003_auto_20161110_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='channel',
            field=models.CharField(blank=True, choices=[('industry', 'Industry'), ('research', 'Research'), ('government', 'Government'), ('other', 'Other biointel'), ('search_engines', 'Search Engines'), ('social', 'Social'), ('general', 'General')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='domains',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='locations',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='status',
            field=models.CharField(blank=True, choices=[('keep', 'Keep'), ('alert', 'Alert'), ('promoted', 'Promoted'), ('trash', 'Trash'), ('raw', 'Raw')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(blank=True, to='tagging.Tag'),
        ),
        migrations.AlterField(
            model_name='article',
            name='article_url',
            field=models.URLField(db_index=True, max_length=2048),
        ),
        migrations.AlterField(
            model_name='article',
            name='body',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='search',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='articles', to='crawl_engine.SearchQuery'),
        ),
        migrations.AlterField(
            model_name='article',
            name='source_language',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(blank=True, db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='article',
            name='translated_body',
            field=models.TextField(blank=True, null=True),
        ),
    ]
