from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from crawl_engine.models import Article
from rest_framework import viewsets
from crawl_engine.serializers import ArticleSerializer, TaskURLSerializer
from crawl_engine.tasks import crawl_url


class ArticleListSet(viewsets.ModelViewSet):

    queryset = Article.objects.all().order_by('-post_date_crawled')
    serializer_class = ArticleSerializer


class AddTaskURLView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = TaskURLSerializer(data=data)
        if serializer.is_valid():
            result = crawl_url.delay(data['url'], data['issue_id'])
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)





