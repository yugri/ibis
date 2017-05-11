from os import path
from unittest.mock import patch, Mock
from django.test import TestCase
from django.core import serializers

from crawl_engine.spiders.single_url_parser import ArticleParser
from crawl_engine.models import Article


class RegressionTestCase(TestCase):
    """ Tests that nothing significant broken while refactoring
    Nothing is actually tested, and test should be removed after text coverage
    """
    def read_sample_file(self, file_name):
        base_dir = path.dirname(path.realpath('__file__'))
        file_path = path.join(base_dir, 'crawl_engine/tests/spiders/sample_data/articles', file_name)
        return open(file_path, "r").read()

    @patch('requests.get')
    def test_nothing_is_broken(self, mock_get):
        # mock response
        mock_response = Mock()
        mock_response.text = self.read_sample_file('industry.html')
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        parser = ArticleParser('http://example.com/industry.html')
        article = Article.objects.get(pk=parser.run())
        print(serializers.serialize('json', [article]))
        self.assertEqual(article.body, article.translated_body)
        self.assertEqual(article.title, article.translated_title)
        self.assertEqual(article.source_language, "en")
        assert len(article.body) > 0
        assert len(article.title) > 0
        assert len(article.top_image_url) > 0
        assert len(article.post_date_created) > 0

    def test__fallback_article_html(self):
        parser = ArticleParser('http://example.com/industry.html')
        html = parser._fallback_article_html(self.read_sample_file('industry.html'))
        assert len(html) > 0
