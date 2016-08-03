from rest_framework.exceptions import ValidationError

from crawl_engine.models import Article
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('article_url', 'title', 'body', 'authors', 'post_date_created',
                  'post_date_crawled')


class TaskURLSerializer(serializers.Serializer):
    url = serializers.CharField(read_only=True)
    issue_id = serializers.CharField(required=False, allow_blank=True, max_length=50)

    def to_internal_value(self, data):
        url_list = data.get('url_list')
        issue_id = data.get('issue_id')
        single = data.get('single')
        custom = data.get('custom')
        query = data.get('query')
        engine = data.get('engine')


        # Validate the data
        # if not url_list or query:
        #     raise ValidationError({
        #         'url': 'This field is required'
        #     })
        # if not issue_id or single or custom or engine:
        #     pass

        return {
            'url': url_list,
            'issue_id': issue_id,
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