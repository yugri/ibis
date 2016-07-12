from django.conf.urls import url, include
from rest_framework import routers
from crawl_engine.views import AddTaskURLView, ArticleListSet


router = routers.DefaultRouter()
router.register(r'articles', ArticleListSet)


urlpatterns = [
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'add-task-url/', AddTaskURLView.as_view()),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
]