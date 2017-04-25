from django.test import TestCase

from crawl_engine.utils.article_processing_utils import is_url_blacklisted
from crawl_engine.models import BlockedSite


class BlacklistTestCase(TestCase):

    def test_block_simple(self):
        BlockedSite.objects.create(ibis_site_id='example_block', site='example2.com')
        self.assertEqual(is_url_blacklisted('https://www.example2.com/some.html'),
                         'example2.com')

    def test_block_subdomain(self):
        BlockedSite.objects.create(ibis_site_id='example_block', site='test1\.example\.com.*')
        self.assertIsNone(is_url_blacklisted('http://test2.exa2mple.com/some.html'))
        self.assertIsNotNone(is_url_blacklisted('http://test1.example.com/some.html'))
