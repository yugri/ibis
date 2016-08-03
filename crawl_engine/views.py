import os.path
import json
import logging
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, filters
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from crawl_engine.models import Article
from rest_framework import viewsets
from crawl_engine.serializers import ArticleSerializer, TaskURLSerializer, TaskURLListSerializer
from crawl_engine.tasks import crawl_url
from pybloomfilter import BloomFilter
from crawl_engine.spiders.search_engines_spiders import SearchEngineParser


logger = logging.getLogger(__name__)


class ArticleListSet(viewsets.ReadOnlyModelViewSet):

    queryset = Article.objects.all().order_by('-post_date_crawled')
    serializer_class = ArticleSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('translated',)


class AddTaskURLView(APIView):

    # renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        bloom_file_path = '/tmp/url.bloom'
        if os.path.exists(bloom_file_path):
            url_filter = BloomFilter.open(bloom_file_path)
        else:
            url_filter = BloomFilter(100000, 0.1, bloom_file_path)
        data = request.data
        single = data.get('single')
        custom = data.get('custom')
        tasks = []

        if single:
            serializer = TaskURLSerializer(data=data)
            if serializer.is_valid():
                url = data['url_list'][0]
                if not url in url_filter:
                    task = crawl_url.delay(url, data['issue_id'])
                    tasks.append(task.id)
                    data['tasks'] = tasks
                    url_filter.add(url)
                else:
                    logger.info('DUPLICATE URL: %s \n REJECTED', url)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif custom:
            serializer = TaskURLSerializer(data=data)
            if serializer.is_valid():
                query = data['query']
                engine = data['engine']
                p = SearchEngineParser(query, engine)
                print(p.search())

        else:
            serializer = TaskURLListSerializer(data=data)
            if serializer.is_valid():

                for url in data['url_list']:
                    if not url in url_filter:
                        task = crawl_url.delay(url, data['issue_id'])
                        tasks.append(task.id)
                        url_filter.add(url)
                    else:
                        logger.info('DUPLICATE URL: %s \n REJECTED', url)
                data['tasks'] = tasks
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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





