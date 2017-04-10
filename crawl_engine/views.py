import json
import logging
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from crawl_engine.common.constants import TYPES
from crawl_engine.spiders.search_engines_spiders import get_search_parser
from crawl_engine.models import Article, SearchQuery, BlockedSite
from crawl_engine.serializers import (ArticleSerializer,
                                      SearchQuerySerializer, BlockedSiteSerializer)
from django.conf import settings


logger = logging.getLogger(__name__)


class ArticlesListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        search_id = self.kwargs['search_id']
        search_instance = get_object_or_404(SearchQuery, search_id=search_id)

        return Article.objects.filter(search_id=search_instance.id)


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
        search_types = TYPES
        return Response(search_types)


class BlockedSitesList(generics.ListCreateAPIView):
    queryset = BlockedSite.objects.all()
    serializer_class = BlockedSiteSerializer


class BlockedSiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlockedSite.objects.all()
    serializer_class = BlockedSiteSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = get_object_or_404(queryset, ibis_site_id=self.kwargs['ibis_site_id'])

        return obj


@api_view(['GET'])
def search_preview(request):
    query = request.query_params.get('q', None)
    engine = request.query_params.get('engine', None)
    try:
        parser = get_search_parser(query, engine, 1)
        return Response(parser.run())
    except Exception as e:
        return Response({'message': str(e)}, status=400)
