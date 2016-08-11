from django.conf.urls import url, include
from rest_framework import routers
from crawl_engine.views import *


router = routers.DefaultRouter()
# router.register(r'articles', ArticleListSet)


urlpatterns = [
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'add-task-url/', AddTaskURLView.as_view()),
    # url(r'articles/', ArticleListSet.as_view({
    #     'get': 'list',
    # })),
    url(r'^get_search_articles/(?P<search_id>[\w-]+)$', ArticlesListView.as_view()),

    url(r'^search_query/$', SearchQueryList.as_view()),
    url(r'^search_query/(?P<search_id>[\w-]+)$', SearchQueryDetailView.as_view()),

    url(r'^source_list/$', ListSources.as_view()),

    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
]