from os import path
from unittest.mock import patch, Mock
from django.test import TestCase

from crawl_engine.spiders.single_url_parser import ArticleParser
from crawl_engine.models import Article, SearchQuery


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
        mock_response.url = 'http://example.com/industry.html'
        mock_get.return_value = mock_response

        search = SearchQuery.objects.create()
        parser = ArticleParser('http://example.com/industry.html', search.pk)
        article = Article.objects.get(pk=parser.run())

        self.assertEqual(article.body, article.translated_body)
        self.assertEqual(article.title, article.translated_title)
        self.assertEqual(article.source_language, "en")
        assert len(article.body) > 0
        assert len(article.title) > 0
        assert len(article.top_image_url) > 0
        assert len(article.post_date_created) > 0
        assert article.search is not None

    @patch('requests.get')
    def test_vietnamese(self, mock_get):
        # mock response
        mock_response = Mock()
        mock_response.text = self.read_sample_file('vietnamese.html')
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.url = 'http://example.com/vietnamese.html'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        parser = ArticleParser('http://example.com/vietnamese.html')
        article = parser.run(save=False)

        self.assertEqual(article.title, "Những tác dụng không tốt của một số thực phẩm khi ăn vào bữa tối")
        assert "Một số thực phẩm khi" in article.body

    def test_empty_response_on_http_error(self):
        parser = ArticleParser('http://httpbin.org/status/403')
        assert 'connection' in parser.run(save=False)

    def test_non_html_with_initial(self):
        parser = ArticleParser('http://httpbin.org/image/jpeg')
        article = parser.run(save=False, initial={'title': 'some title', 'body': 'English'})
        assert article.status == 'trash'
        assert article.title == 'some title'
        assert article.translated_body == '<p>English</p>'
