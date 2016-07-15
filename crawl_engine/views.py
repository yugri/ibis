import json

from django.http import HttpResponse
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from crawl_engine.models import Article
from rest_framework import viewsets
from crawl_engine.serializers import ArticleSerializer, TaskURLSerializer, TaskURLListSerializer
from crawl_engine.tasks import crawl_url


class ArticleListSet(viewsets.ModelViewSet):

    queryset = Article.objects.all().order_by('-post_date_crawled')
    serializer_class = ArticleSerializer


class AddTaskURLView(APIView):

    # renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        # Instantiate UrlsProcessor
        processor = UrlsProcessor()
        data = request.data
        single = data.get('single')
        tasks = []
        if single:
            serializer = TaskURLSerializer(data=data)
            if serializer.is_valid():
                processor = UrlsProcessor()
                task = crawl_url.delay(data['url_list'][0], data['issue_id'])
                tasks.append(task.id)
                data['tasks'] = tasks
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            serializer = TaskURLListSerializer(data=data)
            if serializer.is_valid():

                for url in processor.urls_from_file():
                    task = crawl_url.delay(url, data['issue_id'])
                    tasks.append(task.id)
                data['tasks'] = tasks
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UrlsProcessor:
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





