from os import path
from unittest.mock import patch, Mock
from django.test import TestCase
from crawl_engine.spiders.search_engines_spiders import (
    get_search_parser, YandexParser, BingParser, GoogleParser, GoogleCseParser)


class HelperTestCase(TestCase):

    def test_get_search_parser(self):
        parser = get_search_parser('query', 'google')
        self.assertEqual(type(parser).__name__, 'GoogleParser')


def data_filename(name):
    dir = path.dirname(path.realpath('__file__'))
    return path.join(dir, 'crawl_engine/tests/spiders/sample_data/', name)


class YandexParserTestCase(TestCase):

    @patch('urllib.request.urlopen')
    def test_run(self, mock_urlopen):
        reply = open(data_filename("yandex.xml"), "r").read()
        mock = Mock()
        mock.read.return_value = reply
        mock_urlopen.return_value = mock

        parser = YandexParser('testing more', 1, None)
        result = parser.run()
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]['url'], 'https://yandex.ru/')
        self.assertEqual(result[0]['title'],
                         'Яндекс\n              \n              — поисковая система и интернет-портал')
        self.assertGreater(len(result[6]['text']), 0)


def mock_requests_get(filename):
    reply = open(data_filename(filename), "r").read()
    mock = Mock()
    mock.text = reply
    return mock


class BingParserTestCase(TestCase):

    @patch('requests.get')
    def test_run(self, mock_get):
        mock_get.return_value = mock_requests_get('bing.html')

        parser = BingParser('testing more', 1, None)
        result = parser.run()
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]['url'], 'https://www.speedtest.net/')
        self.assertEqual(result[0]['title'], 'Speedtest.net - Official Site')
        self.assertGreater(len(result[0]['text']), 0)


class GoogleCseParserTestCase(TestCase):

    @patch('requests.get')
    def test_run(self, mock_get):
        mock_get.return_value = mock_requests_get('google_cse.json')

        parser = GoogleCseParser('testing more', 1, None)
        result = parser.run()
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]['url'], 'https://perldoc.perl.org/Test/More.html')
        self.assertEqual(result[0]['title'], 'Test::More - perldoc.perl.org')
        self.assertGreater(len(result[0]['text']), 0)


class GoogleParserTestCase(TestCase):

    @patch('requests.get')
    def test_run(self, mock_get):
        mock_get.return_value = mock_requests_get('google.html')
        parser = GoogleParser('testing more', 1, None)
        result = parser.run()
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]['url'], 'https://perldoc.perl.org/Test/More.html')
        self.assertEqual(result[0]['title'], 'Test::More - perldoc.perl.org')
        self.assertGreater(len(result[0]['text']), 0)