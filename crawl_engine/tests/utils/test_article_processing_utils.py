import pytest
from django.test import TestCase

from crawl_engine.exceptions import BlacklistedURLException
from crawl_engine.utils.article_processing_utils import is_url_blacklisted
from crawl_engine.models import BlockedSite


class BlacklistTestCase(TestCase):

    def test_block_domain(self):
        BlockedSite.objects.create(ibis_site_id='example_block', site='example\.com.*')
        with pytest.raises(BlacklistedURLException):
            is_url_blacklisted('http://example.com/some.html')

    def test_block_subdomain(self):
        BlockedSite.objects.create(ibis_site_id='example_block', site='test1\.example\.com.*')
        is_url_blacklisted('http://test2.exa2mple.com/some.html')
        with pytest.raises(BlacklistedURLException):
            is_url_blacklisted('http://test1.example.com/some.html')
