import os.path
import json
import logging
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from crawl_engine.models import Article, SearchQuery
from crawl_engine.serializers import ArticleSerializer, TaskURLSerializer, TaskURLListSerializer, SearchQuerySerializer
from crawl_engine.tasks import crawl_url
from crawl_engine.spiders.search_engines_spiders import SearchEngineParser
from django.conf import settings


logger = logging.getLogger(__name__)


class ArticlesListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        search_id = self.kwargs['search_id']
        search_instance = get_object_or_404(SearchQuery, search_id=search_id)

        return Article.objects.filter(search_id=search_instance.id)


# class AddTaskURLView(APIView):
#
#     def post(self, request, *args, **kwargs):
#         bloom_file_path = settings.BASE_DIR + '/url.bloom'
#         if os.path.exists(bloom_file_path):
#             url_filter = BloomFilter.open(bloom_file_path)
#         else:
#             url_filter = BloomFilter(10000000, 0.1, bloom_file_path)
#         data = request.data
#         single = data.get('single')
#         custom = data.get('custom')
#         tasks = []
#
#         if single:
#             serializer = TaskURLSerializer(data=data)
#             if serializer.is_valid():
#                 url = data['url_list'][0]
#                 if not url in url_filter:
#                     task = crawl_url.delay(url, data['search_id'])
#                     tasks.append(task.id)
#                     data['tasks'] = tasks
#                     url_filter.add(url)
#                 else:
#                     logger.info('DUPLICATE URL: %s \n REJECTED', url)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         elif custom:
#             serializer = TaskURLSerializer(data=data)
#             if serializer.is_valid():
#                 query = data['query']
#                 engine = data['engine']
#                 p = SearchEngineParser(query, engine)
#                 links_to_crawl = p.run()
#                 for url in links_to_crawl:
#                     if not url in url_filter:
#                         task = crawl_url.apply_async((url, data['search_id']), countdown=10)
#                         tasks.append(task.id)
#                         url_filter.add(url)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         else:
#             serializer = TaskURLListSerializer(data=data)
#             if serializer.is_valid():
#
#                 for url in data['url_list']:
#                     if not url in url_filter:
#                         task = crawl_url.apply_async((url, data['search_id']), countdown=10)
#                         tasks.append(task.id)
#                         url_filter.add(url)
#                     else:
#                         logger.info('DUPLICATE URL: %s \n REJECTED', url)
#                 data['tasks'] = tasks
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UrlsProcessor:
    """
    Only for demonstration use
    """
    urls = ''

    def urls_from_file(self, file='/home/yuri/dev/ibis_crawl_engine/items_news_keywords_13.json'):
        urls_list = []
        f = open(file)
        output = json.load(f)
        for item in output:
            urls_list.append(item['link'])
        return urls_list


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class SearchQueryList(generics.ListCreateAPIView):
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer
    filter_fields = []

    def perform_create(self, serializer):
        # Add additional field to the request.data. Client host address in our case
        # and save serializer
        response_address = self.request.META.get('REMOTE_ADDR', None)
        serializer.save(response_address=response_address)


class SearchQueryDetailView(generics.RetrieveUpdateAPIView):
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = get_object_or_404(queryset, search_id=self.kwargs['search_id'])

        return obj


class ListSources(APIView):

    def get(self, request, format=None):
        """
        Return a list of all sources.
        """
        sources = [source for source in settings.SOURCES]
        return Response(sources)


class ListSearchTypes(APIView):

    def get(self, request, format=None):
        """
        Return a list of all search types.
        """
        search_types = SearchQuery.TYPES
        return Response(search_types)