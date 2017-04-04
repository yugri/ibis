from django.test import TestCase
from crawl_engine.spiders.search_engines_spiders import get_search_parser


class HelperTestCase(TestCase):

    def test_get_search_parser(self):
        parser = get_search_parser('query', 'google')
        self.assertEqual(type(parser).__name__, 'GoogleParser')
