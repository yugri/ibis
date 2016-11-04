# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-04 08:08
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_url', models.URLField(db_index=True, max_length=1000)),
                ('source_language', models.CharField(blank=True, max_length=5, null=True)),
                ('title', models.CharField(blank=True, max_length=1000)),
                ('translated_title', models.CharField(blank=True, max_length=1000)),
                ('body', models.TextField(blank=True)),
                ('translated_body', models.TextField(blank=True)),
                ('authors', models.CharField(blank=True, max_length=1000)),
                ('post_date_created', models.CharField(blank=True, max_length=50)),
                ('post_date_crawled', models.DateTimeField(auto_now_add=True, null=True)),
                ('translated', models.BooleanField(db_index=True, default=False)),
                ('top_image_url', models.URLField(blank=True, max_length=1000)),
                ('top_image', models.ImageField(blank=True, max_length=1000, null=True, upload_to='article-images')),
                ('file', models.FileField(blank=True, null=True, upload_to='article-files')),
                ('processed', models.BooleanField(db_index=True, default=False)),
                ('pushed', models.BooleanField(db_index=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_id', models.CharField(db_index=True, max_length=50)),
                ('search_type', models.CharField(choices=[('simple_search', 'Simple Search'), ('search_engine', 'Advanced Search'), ('rss', 'RSS Feed'), ('article', 'Article'), ('email', 'Email')], default='search_engine', max_length=20)),
                ('article_url', models.CharField(blank=True, max_length=1000, null=True)),
                ('rss_link', models.CharField(blank=True, max_length=1000, null=True)),
                ('query', models.TextField(blank=True)),
                ('source', models.CharField(choices=[('google', 'Google'), ('google_cse', 'Google CSE'), ('google_blogs', 'Google Blogs'), ('google_news', 'Google News'), ('google_scholar', 'Google Scholar'), ('bing', 'Bing'), ('yandex', 'Yandex')], default='google', max_length=15)),
                ('search_depth', models.PositiveIntegerField(default=10)),
                ('active', models.BooleanField(default=True)),
                ('period', models.CharField(choices=[('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='daily', max_length=20)),
                ('last_processed', models.DateTimeField(blank=True, null=True)),
                ('response_address', models.CharField(blank=True, max_length=50, null=True)),
                ('options', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchTask',
            fields=[
                ('task_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('search_query', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='crawl_engine.SearchQuery')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='search',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crawl_engine.SearchQuery'),
        ),
    ]
