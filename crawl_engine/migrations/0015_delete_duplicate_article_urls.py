# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 12:07
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    # Remove aritcles with dupliacte article_url
    Article = apps.get_model("crawl_engine", "Article")
    db = schema_editor.connection.alias
    print('\nDeleting duplicates:')
    for row in Article.objects.using(db).all():
        if Article.objects.using(db).filter(article_url=row.article_url).count() > 1:
            row.delete()
            print('\tDeleted article with url "%s"' % row.article_url)


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_engine', '0014_auto_20170509_1234'),
    ]

    operations = [
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]