from django.contrib import admin

from tagging.models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'id']
    search_fields = ['name']


admin.site.register(Tag, TagAdmin)
