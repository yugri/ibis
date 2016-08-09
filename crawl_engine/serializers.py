from rest_framework.exceptions import ValidationError

from crawl_engine.models import Article, SearchQuery
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('article_url', 'title', 'body', 'authors', 'post_date_created',
                  'post_date_crawled')


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


        # Validate the data
        # if not url_list or query:
        #     raise ValidationError({
        #         'url': 'This field is required'
        #     })
        # if not search_id or single or custom or engine:
        #     pass

        return {
            'url': url_list,
            'search_id': search_id,
            'single': single,
            'custom': custom,
            'query': query,
            'engine': engine
        }


# class SearchQuerySerializer(serializers.Serializer):
#     urls = URLListField(allow_empty=True)
#     query = serializers.CharField(allow_blank=True)
#     engines = serializers.ListField(allow_empty=True)
#     search_id = serializers.CharField(required=True)
#
#     def to_internal_value(self, data):
#         urls = data.get('urls')
#         search_id = data.get('search_id')
#         query = data.get('query')
#         engines = data.get('engine')
#
#         return {
#             'url': urls,
#             'search_id': search_id,
#             'query': query,
#             'engine': engines
#         }


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


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery