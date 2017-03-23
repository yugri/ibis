from crawl_engine import tasks
from django.contrib import admin
from crawl_engine.models import Article, SearchQuery, SearchTask


def mark_as_non_pushed(modeladmin, request, queryset):
    queryset.update(pushed=False)
mark_as_non_pushed.short_description = "Mark selected articles as NOT pushed"


def mark_as_processed(modeladmin, request, queryset):
    queryset.update(processed=True)
mark_as_processed.short_description = "Mark selected articles as processed"


class TasksAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'tstamp']
    ordering = ['tstamp']
    actions = ['crawl_url']


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'translated', 'post_date_crawled', 'search_id', 'short_url']
    list_filter = ('translated', 'processed', 'pushed')
    search_fields = ('search__search_id', 'article_url')
    actions = [mark_as_non_pushed, mark_as_processed]


class SearchTaskInline(admin.TabularInline):
    model = SearchTask


class SearchQueryAdmin(admin.ModelAdmin):
    inlines = [
        SearchTaskInline
    ]
    list_display = ('search_type', 'query', 'rss_link', 'article_url', 'active', 'period', 'last_processed')
    list_display_links = ('search_type', 'query')


admin.site.register(Article, ArticleAdmin)
admin.site.register(SearchQuery, SearchQueryAdmin)