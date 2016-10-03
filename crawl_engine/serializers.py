import json

from rest_framework.exceptions import ValidationError

from crawl_engine.models import Article, SearchQuery
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article


class ArticleTransferSerializer(serializers.ModelSerializer):
    search_id = serializers.SerializerMethodField()
    # related_search_id = serializers.CharField(required=False, default='5c15f2a9-b89a-4c0c-b7b5-b0eb38607b2c')
    # search_id = serializers.CharField(required=False, default='46268d29-ebff-4614-b045-f28bc673f6cf')

    class Meta:
        model = Article
        fields = ('article_url', 'source_language', 'title', 'translated_title', 'body', 'translated_body',
                  'authors', 'post_date_created', 'translated', 'top_image_url', 'top_image',
                  'processed', 'search_id')
        # exclude = ('search', 'pushed')

    def get_search_id(self, obj):
        return '370f81e7-199d-4901-9dbf-47edf6a59f05'



class URLListField(serializers.ListField):
    child = serializers.URLField()


class TaskURLSerializer(serializers.Serializer):
    url = serializers.CharField(read_only=True)
    issue_id = serializers.CharField(required=False, allow_blank=True, max_length=50)

    def to_internal_value(self, data):
        url_list = data.get('url_list')
        search_id = data.get('search_id')
        single = data.get('single')
        custom = data.get('custom')
        query = data.get('query')
        engine = data.get('engine')

        return {
            'url': url_list,
            'search_id': search_id,
            'single': single,
            'custom': custom,
            'query': query,
            'engine': engine
        }


class TaskURLListSerializer(serializers.Serializer):
    url_list = serializers.CharField(read_only=True)
    issue_id = serializers.CharField(required=False, allow_blank=True, max_length=50)

    def to_internal_value(self, data):
        url_list = data.get('url_list')
        issue_id = data.get('issue_id')

        #Validate the data
        if not url_list or not isinstance(url_list, list):
            raise ValidationError({
                'url_list': 'You should specify the url\'s list'
            })
        if not issue_id:
            pass

        return {
            'url_list': url_list,
            'issue_id': issue_id
        }


class OptionsSerializer(serializers.Serializer):
    exactTerms = serializers.CharField(allow_blank=True)
    excludeTerms = serializers.CharField(allow_blank=True)

    def to_representation(self, obj):
        options = json.loads(obj)
        return {
            'exactTerms': options['exactTerms'],
            'excludeTerms': options['excludeTerms']
        }

    def to_internal_value(self, data):
        options = json.dumps(data)
        return options


class SearchQuerySerializer(serializers.ModelSerializer):
    options = OptionsSerializer(required=False)

    class Meta:
        model = SearchQuery