from django.test import TestCase

from unittest.mock import patch
from crawl_engine.tasks import crawl_url


class CrawlUrlTestCase(TestCase):

    @patch('crawl_engine.tasks.is_url_blacklisted')
    def test_crawl_blocked(self, mock_is_url_blacklisted):
        mock_is_url_blacklisted.return_value = 'example.com'

        self.assertEqual(crawl_url('https://www.example.com/some.html'),
                         'Blacklisted resource "example.com" found.')
