import base64
import json
import logging
from ipware.ip import get_ip

from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from crawl_engine.common.constants import TYPES
from crawl_engine.spiders.single_url_parser import ArticleParser
from crawl_engine.spiders.search_engines_spiders import get_search_parser
from crawl_engine.models import Article, SearchQuery, TrashFilter
from crawl_engine.serializers import (ArticleSerializer,
                                      SearchQuerySerializer, TrashFilterSerializer)
from django.conf import settings


logger = logging.getLogger(__name__)


class ArticlesListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        search_id = self.kwargs['search_id']
        search_instance = get_object_or_404(SearchQuery, search_id=search_id)

        return Article.objects.filter(search_id=search_instance.id)


class ArticleView(generics.RetrieveAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def get_object(self):
        article_encoded_url = self.kwargs['article_encoded_url']
        decoded_url = base64.b64decode(article_encoded_url)
        queryset = self.filter_queryset(self.get_queryset())
        article_url = str(decoded_url, 'utf-8')

        obj = get_object_or_404(queryset, article_url=article_url)

        return obj


class IndexView(View):

    def get(self, request):
        return render(
            request,
            'index.html',
            {}
        )


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


class SearchQueryList(generics.ListCreateAPIView):
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer
    filter_fields = []

    def perform_create(self, serializer):
        # Add additional field to the request.data. Client host address in our case
        # and save serializer
        serializer.save(response_address=get_ip(self.request))


class SearchQueryDetailView(generics.RetrieveUpdateDestroyAPIView):
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
        search_types = TYPES
        return Response(search_types)


class TrashFilterList(generics.ListCreateAPIView):
    queryset = TrashFilter.objects.all()
    serializer_class = TrashFilterSerializer


class TrashFilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrashFilter.objects.all()
    serializer_class = TrashFilterSerializer


@api_view(['POST'])
def reset_status(request):
    url = request.data.get('url', None)
    article = get_object_or_404(Article, article_url=url)
    return Response({'status': article.reset_initial_status()})


@api_view(['GET'])
def parser_preview(request):
    url = request.META.get('QUERY_STRING', None)
    if url is None:
        return Response({'message': 'add "?http://sample.com/" param'}, status=400)

    parser = ArticleParser(url)
    article = parser.run(save=False)
    serializer = ArticleSerializer(article)

    return Response(serializer.data)


@api_view(['GET'])
def search_preview(request):
    query = request.query_params.get('q', None)
    engine = request.query_params.get('engine', None)
    try:
        parser = get_search_parser(query, engine, 1)
        return Response(parser.run())
    except Exception as e:
        return Response({'message': str(e)}, status=400)
