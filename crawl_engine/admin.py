from crawl_engine import tasks
from django.contrib import admin
from crawl_engine.models import Article


class TasksAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'tstamp']
    ordering = ['tstamp']
    actions = ['crawl_url']


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['article_url', 'title', 'authors']


admin.site.register(Article, ArticleAdmin)