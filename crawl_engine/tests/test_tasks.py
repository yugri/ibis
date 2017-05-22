import pytest
from unittest.mock import patch, Mock
from django.test import TestCase
from crawl_engine.tasks import crawl_url


class CrawlUrlTestCase(TestCase):

    @patch('crawl_engine.spiders.single_url_parser.ArticleParser.run')
    def test_crawl_url_with_url(self, run_mock):
        run_mock.return_value = '123'

        self.assertEqual(crawl_url('http://example.com/'), '123')
        run_mock.assert_called_with(save=True, initial={'article_url': 'http://example.com/'})

    @patch('crawl_engine.spiders.single_url_parser.ArticleParser.run')
    def test_crawl_url_with_intial(self, run_mock):
        intial = {'article_url': 'http://example.com/', 'title': 'title'}
        run_mock.return_value = '123'

        self.assertEqual(crawl_url(intial), '123')
        run_mock.assert_called_with(save=True, initial=intial)
