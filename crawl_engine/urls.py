from django.conf.urls import url, include
from rest_framework import routers
import crawl_engine.views as views


router = routers.DefaultRouter()

urlpatterns = [
    url(r'^get_search_articles/(?P<search_id>[\w-]+)$', views.ArticlesListView.as_view()),
    url(r'^article/(?P<article_url>.+)/$', views.ArticleView.as_view()),

    url(r'^search_query/$', views.SearchQueryList.as_view()),
    url(r'^search_query/(?P<search_id>[\w-]+)$', views.SearchQueryDetailView.as_view()),

    url(r'^source_list/$', views.ListSources.as_view()),
    url(r'^search_types_list/$', views.ListSearchTypes.as_view()),

    url(r'^blocked_sites/$', views.BlockedSitesList.as_view()),
    url(r'^blocked_sites/(?P<ibis_site_id>[\w-]+)$', views.BlockedSiteDetailView.as_view()),

    url(r'^preview$', views.search_preview),
    url(r'^$', views.IndexView.as_view()),

    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
]
