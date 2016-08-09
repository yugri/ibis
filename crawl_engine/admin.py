from crawl_engine import tasks
from django.contrib import admin
from crawl_engine.models import Article, SearchQuery


class TasksAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'tstamp']
    ordering = ['tstamp']
    actions = ['crawl_url']


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['article_url', 'title', 'authors', 'translated', 'post_date_crawled', 'search_id']
    list_filter = ('translated',)


admin.site.register(Article, ArticleAdmin)
admin.site.register(SearchQuery)