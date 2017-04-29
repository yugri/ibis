import logging
import json
import feedparser

from random import randint
from time import sleep

from django.conf import settings
import lxml.html
import requests
from urllib.parse import parse_qs, urlparse, unquote
from crawl_engine.spiders.ya_search import YaSearch


logger = logging.getLogger(__name__)


def xpath_first(item, path):
    """ method for safelly get first element """
    items = item.xpath(path)
    return items[0] if len(items) > 0 else ""


def xpath_first_text(item, path):
    """ method for safelly get first element text_content() """
    item = xpath_first(item, path)
    return item.text_content() if item != "" else ""


class ParserError(Exception):
    pass


class SearchParser:
    """ Base class for search engine parsers """
    def __init__(self, search_query, depth, options):
        self.search_query = search_query
        self.depth = depth
        self.options = options

    def _new_article(self, url, title, text):
        """ Probably replace this with Article models """
        return {'url': url.strip(), 'title': title.strip(), 'text': text.strip()}


class GoogleGeneralParser(SearchParser):
    """
    BAse class for parsing google search results
    """
    def _parse_href(self, href):
        """
        Revise this method
        """
        # Method for normalising Google's result link. Receives the link, parse it and gets the direct
        # url from querystring. E.g.: google's result links look's like:
        # https://www.google.com/url?q=some+query&url=http://foo.bar.url
        # so we should get only q parameter from google's querystring
        try:
            url = parse_qs(urlparse(href).query)['q'][0]
            return unquote(url)
        except KeyError:
            return href

    def _get_tree(self, url, params):
        sleep(randint(1, 2))
        r = requests.get(url, params)
        tree = lxml.html.fromstring(r.text)

        if "Google" not in tree.findtext('.//title'):
            logger.info("I can't find Google in page title")

        return tree


class GoogleParser(GoogleGeneralParser):

    def run(self):
        base_url = 'https://google.com/search'
        result = []
        for count in range(0, self.depth):
            tree = self._get_tree(base_url, {'q': self.search_query, 'start': count * 10, 'sa': 'N'})

            for item in tree.xpath("//div[@class='g']"):
                result.append(self._new_article(
                    self._parse_href(xpath_first(item, ".//a/@href")),
                    xpath_first_text(item, ".//a"),
                    xpath_first_text(item, ".//span[@class='st']")
                ))

        return result


class GoogleScholarParser(GoogleGeneralParser):
    """
    Class for fetching results from google's scholar.google.com.
    Search query example: https://scholar.google.com.ua/scholar?start=30&q=robotics+ai&start=30
    start parameter responsible for results pagination
    :return: seed_links
    """
    def run(self):
        base_url = 'https://scholar.google.com/scholar'
        result = []
        for count in range(0, self.depth):
            tree = self._get_tree(base_url, {'q': self.search_query, 'start': count * 10, 'sa': 'N'})

            for item in tree.xpath("//div[@class='gs_ri']"):
                if (len(item.xpath(".//a/@href")) == 0) or (len(item.xpath(".//div[@class='gs_rs']")) == 0):
                    continue
                result.append(self._new_article(
                    self._parse_href(xpath_first(item, ".//a/@href")),
                    xpath_first_text(item, ".//a"),
                    xpath_first_text(item, ".//div[@class='gs_rs']")
                ))

        return result


class GoogleNewsParser(SearchParser):
    """
    Gets results from google's news.google.com and parses all them by feedparser
    Search query example: https://news.google.com/news/feeds?output=rss&q=banking&num=30.
    num parameter responsible for the number of returned entries (max=30, default=30)
    output parameter responsible for response format (ATOM or RSS)
    :return: seed_links
    """
    def _parse_href(self, href):
        """
        Revise this method
        """
        # Method for normalising Google's result link. Receives the link, parse it and gets the direct
        # url from querystring. E.g.: google's result links look's like:
        # https://www.google.com/url?q=some+query&url=http://foo.bar.url
        # so we should get only q parameter from google's querystring
        try:
            url = parse_qs(urlparse(href).query)['url'][0]
            return unquote(url)
        except KeyError:
            return href

    def run(self):
        base_url = 'https://news.google.com/news'
        r = requests.get(base_url, {'q': self.search_query, 'output': 'rss', 'num': self.depth * 10})
        feed = feedparser.parse(r.text)

        return [self._new_article(self._parse_href(entry.link), entry.title, entry.description)
                for entry in feed.entries]


class GoogleCseParser(SearchParser):
    """
    Another method for getting google's search results but from CSE (custom search engine):
    https://developers.google.com/custom-search/json-api/v1/using_rest.
    Using Requests library
    :return: seed_links list
    """

    def __init__(self, search_query, depth, options):
        # Check search depth value if it higher than 10
        # redefine it to display only 100 first results
        # see: https://developers.google.com/custom-search/json-api/v1/using_rest
        if depth > 10:
            logger.warn("Only the first 100 results will be displayed, due to CSE search depth limit.")
            depth = 10

        # We store options at JSONField. So we need to load them.
        options = json.loads(options) if options else None

        super(GoogleCseParser, self).__init__(search_query, depth, options)

    def run(self):
        base_url = 'https://www.googleapis.com/customsearch/v1'
        result = []

        for count in range(0, self.depth):
            params = {
                'key': settings.GOOGLE_TRANSLATE_API_KEY,
                'cx': settings.CSE_ID,
                'q': self.search_query,
                'safe': 'medium',
                'start': count * 10 + 1
            }
            if self.options:
                params.update(self.options)

            r = requests.get(base_url, params=params)
            data = json.loads(r.text)
            if 'items' not in data:
                return []

            for item in data['items']:
                result.append(self._new_article(
                    item['link'],
                    item['title'],
                    item['snippet']
                ))

        return result


class GoogleBlogsParser(GoogleGeneralParser):

    def run(self):

        base_url = 'https://google.com/search'
        result = []
        for count in range(0, self.depth):
            tree = self._get_tree(base_url, {'q': self.search_query, 'start': count * 10, 'tbm': 'nws', 'tbs': 'nrt:b'})

            for item in tree.xpath("//div[@class='g']"):
                result.append(self._new_article(
                    self._parse_href(xpath_first(item, ".//a/@href")),
                    xpath_first_text(item, ".//a"),
                    xpath_first_text(item, ".//div[@class='st']")
                ))

        return result


class BingParser(SearchParser):

    def run(self):
        base_url = 'https://www.bing.com/search'
        result = []
        for count in range(0, self.depth):
            r = requests.get(base_url, {'q': self.search_query, 'first': count * 10 + 1})

            tree = lxml.html.fromstring(r.text)

            if "Bing" not in tree.findtext('.//title'):
                logger.info("I can't find Bing in page title")

            for item in tree.xpath("//li[contains(@class, 'b_algo')]"):
                result.append(self._new_article(
                    xpath_first(item, ".//a/@href"),
                    xpath_first_text(item, ".//a"),
                    xpath_first_text(item, ".//p")
                ))

        return result


class YandexParser(SearchParser):

    def run(self):
        search = YaSearch(settings.YANDEX_API_USER, settings.YANDEX_API_KEY, 'com')
        results = search.search(self.search_query)
        if results.error is not None:
            raise ParserError(results.error.description)

        return [self._new_article(i.url, i.title, i.snippet) for i in results.items]


class SocialParser(SearchParser):

    def run(self):
        base_url = 'https://api.social-searcher.com/v2/search'
        r = requests.get(base_url,
                         {'q': self.search_query,
                          'key': settings.SOCIAL_SEARCHER_API_KEY,
                          'limit': self.depth * 10}, verify=False)
        posts = json.loads(r.text).get('posts')
        if posts is None:
            raise ParserError('Social search returned empty result')
        return [self._new_article(
                    post.get('url'),
                    post.get('network') + ' - @' + post.get('user', {}).get('name'),
                    post.get('text'))
                for post in posts]


SEARCH_PARSERS = {
    'google': GoogleParser,
    'google_scholar': GoogleScholarParser,
    'google_news': GoogleNewsParser,
    'google_cse': GoogleCseParser,
    'google_blogs': GoogleBlogsParser,
    'bing': BingParser,
    'yandex': YandexParser,
    'social': SocialParser,
}


def get_search_parser(search_query, engine, depth=5, options=None):
    """ Init serach parser by name """
    if engine not in SEARCH_PARSERS:
        raise NameError('Search engine %s not found' % engine)
    return SEARCH_PARSERS[engine](search_query, depth, options)


class SearchEngineParser(object):
    """ Backward compatibility layer for parsers """
    def __init__(self, search_query, engine='google', depth=5, options=None):
        self.search_query = search_query
        self.engine = engine
        self.parser = get_search_parser(search_query, engine, depth, options)

    def run(self):
        print(__name__)
        try:
            return [a.get('url') for a in self.parser.run()]
        except Exception as e:
            logger.info('Exception while parsing query "{0}" in search engine "{1}": {2}'.format(
                       self.search_query, self.engine, str(e)))

        return []
