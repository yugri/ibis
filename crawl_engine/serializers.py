import json

from django.conf import settings
from rest_framework.exceptions import ValidationError

from crawl_engine.models import Article, SearchQuery
from rest_framework import serializers

from tagging.models import Tag


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        # exclude = ('id',)
        fields = ('name',)


class ArticleTransferSerializer(serializers.ModelSerializer):
    search_id = serializers.SerializerMethodField()
    # related_search_id = serializers.CharField(required=False, default='5c15f2a9-b89a-4c0c-b7b5-b0eb38607b2c')
    # search_id = serializers.CharField(required=False, default='46268d29-ebff-4614-b045-f28bc673f6cf')
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Article
        fields = ('article_url', 'source_language', 'title', 'translated_title', 'body', 'translated_body',
                  'authors', 'post_date_created', 'post_date_crawled', 'translated', 'top_image_url', 'top_image',
                  'processed', 'search_id', 'channel', 'status', 'locations', 'tags',)
        read_only_fields = ('tags',)
        # exclude = ('search', 'pushed')

    def get_search_id(self, obj):
        try:
            return obj.search.search_id
        except AttributeError:
            pass


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
    response_address = serializers.CharField(required=False)

    def validate_source(self, value):
        source_choices = [x[0] for x in settings.SOURCES]
        for source in value.split(', '):
            if source not in source_choices:
                raise serializers.ValidationError("Can't resolve a source type: %s. "
                                                  "Choices are: %s" % (source, str(source_choices)))
        return value

    class Meta:
        model = SearchQuery
        fields = '__all__'