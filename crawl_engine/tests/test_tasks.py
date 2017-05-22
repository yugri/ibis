import pytest
from unittest.mock import patch, Mock
from django.test import TestCase
from crawl_engine.tasks import crawl_url, search_by_query
from crawl_engine.spiders.search_parser import ParserError


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


class SearchByQueryTestCase(TestCase):

    @patch('crawl_engine.tasks.get_search_parser')
    def test_extracts_url_from_parser(self, mock_get_search_parser):
        mock = Mock()
        mock.run.return_value = [{'article_url': 'http://example.com'}]
        mock_get_search_parser.return_value = mock
        self.assertEqual(search_by_query('test', 'google', 1, {}), mock.run.return_value)

    @patch('crawl_engine.tasks.get_search_parser')
    def test_logs_exception(self, mock_get_search_parser):
        mock = Mock()
        mock.run.return_value = []
        mock.run.side_effect = ParserError('error')
        mock_get_search_parser.return_value = mock
        with self.assertLogs('crawl_engine.tasks', level='INFO'):
            self.assertEqual(search_by_query('test', 'google', 1, {}), [])
