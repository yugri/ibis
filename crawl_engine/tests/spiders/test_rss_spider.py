from test_search_engines_spiders import mock_requests_get
from unittest.mock import patch
from django.test import TestCase
from crawl_engine.spiders.rss_spider import RSSFeedParser
from datetime import datetime


class RSSFeedParserTestCase(TestCase):

    @patch('requests.get')
    def test_run(self, mock_get):
        mock_get.return_value = mock_requests_get('rss.xml')

        parser = RSSFeedParser('http://example.com/rss.xml')
        result = parser.run()
        self.assertEqual(len(result), 9)
        self.assertEqual(
            result[0]['article_url'],
            'http://www.oie.int/wahis_2/public/wahid.php/Reviewreport/Review?reportid=23744')
        self.assertEqual(result[0]['title'], 'Niger : Anthrax')
        self.assertEqual(
            result[0]['body'],
            'Report date : 2017-05-17 16:34:10<br />Country : Niger<br />Disease: : Anthrax')
        self.assertEqual(
            result[0]['post_date_created'],
            datetime(2017, 5, 17, 16, 36, 27))
