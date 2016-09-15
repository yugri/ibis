import json

from rest_framework.exceptions import ValidationError

from crawl_engine.models import Article, SearchQuery
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article


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


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        extra_kwargs = {'search_depth': {'required': 'False'}}

    options = OptionsSerializer(required=False)

    def create(self, validated_data):
        options_dict = validated_data.pop('options')
        search = SearchQuery.objects.create(
            search_id=validated_data['search_id'],
            query=validated_data['query'],
            source=validated_data['source'],
            search_depth=validated_data['search_depth'],
            # search_depth=3,
            active=validated_data['active'],
            period=validated_data['period'],
            last_processed=validated_data['last_processed'],
            options=json.dumps(options_dict)
        )
        return search