from crawl_engine import tasks
from django.contrib import admin
from crawl_engine.models import Article, SearchQuery, SearchTask


class TasksAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'tstamp']
    ordering = ['tstamp']
    actions = ['crawl_url']


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['article_url', 'title', 'authors', 'translated', 'post_date_crawled', 'search_id']
    list_filter = ('translated',)


class SearchTaskInline(admin.TabularInline):
    model = SearchTask


class SearchQueryAdmin(admin.ModelAdmin):
    inlines = [
        SearchTaskInline
    ]
    list_display = ("query", "active", "period", "last_processed")


admin.site.register(Article, ArticleAdmin)
admin.site.register(SearchQuery, SearchQueryAdmin)
