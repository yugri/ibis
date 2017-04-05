import logging
import json
from random import randint
from time import sleep

from django.conf import settings
import lxml.html
import requests
from urllib.parse import quote, parse_qs, urlparse, unquote

from crawl_engine.spiders.rss_spider import RSSFeedParser

logger = logging.getLogger(__name__)


class MaxSearchDepthError(Exception):
    pass


class SearchParser:
    """ Base class for search engine parsers """
    def __init__(self, search_query, depth, options):
        self.search_query = search_query
        self.depth = depth
        self.options = options

    def new_article(url, title, text):
        """ Probably replace this with Article models """
        return {'url': url, 'title': title, 'text': text}


class GoogleParser(SearchParser):
    pass


class GoogleScholarParser(SearchParser):
    pass


class GoogleNewsParser(SearchParser):
    pass


class GoogleCseParser(SearchParser):
    pass


class GoogleBlogsParser(SearchParser):
    pass


class BingParser(SearchParser):
    pass


class YandexParser(SearchParser):
    def run(self):
        result = []
        for count in range(0, self.depth):
            url = 'https://www.yandex.com/search/'
            r = requests.get(url, params={'text': self.search_query, 'p': count})
            tree = lxml.html.fromstring(r.text)

            for div in tree.xpath("//div[contains(@class, 'organic ')]"):
                result.append({
                    'url': div.xpath('.//h2/a/@href')[0],
                    'title': div.xpath('.//h2/a')[0].text_content()
                })

        return result


SEARCH_PARSERS = {
    'google': GoogleParser,
    'google_scholar': GoogleScholarParser,
    'google_news': GoogleNewsParser,
    'google_cse': GoogleCseParser,
    'google_blogs': GoogleBlogsParser,
    'bing': BingParser,
    'yandex': YandexParser
}


def get_search_parser(search_query, engine, depth=5, options=None):
    """ Init serach parser by name """
    return SEARCH_PARSERS[engine](search_query, depth, options)


class SearchEngineParser(object):

    engines_payload = {
        'google': {
            'url': 'https://google.com/search',
            'key': 'q',
            'init_url': 'https://google.com'
        },
        'google_scholar': {
            'url': 'https://scholar.google.com.ua/scholar',
            'key': 'q',
        },
        'google_news': {
            'url': 'https://news.google.com/news',
            'key': 'q',
        },
        'google_cse': {
            'url': 'https://www.googleapis.com/customsearch/v1',
            'key': 'q'
        },
        'google_blogs': {
            'url': 'https://google.com/search',
            'key': 'q',
            'init_url': 'https://google.com'
        },
        'bing': {'url': 'https://www.bing.com/search', 'key': 'q'},
        'yandex': {'url': 'https://www.yandex.ua/search/', 'key': 'text'}
    }
    html = ''
    tree = ''
    depth = None  # The crawling depth

    def __init__(self, search_query, engine='google', depth=5, options=None):
        # Build query dict at init
        if engine == 'google' or engine == 'yandex' or engine == 'google_news':
            search_query = "+".join(search_query.split())
        elif search_query == 'google_cse':
            search_query = search_query
        elif engine == 'yandex':
            search_query = quote(search_query)

        self.engine = engine
        self.url = self.engines_payload[engine]['url']
        self.search_query = search_query
        self.payload = {
            self.engines_payload[engine]['key']: search_query
        }
        self.depth = depth
        self.next_page_xpath = ''
        self.options = options

        # Seed links fetched from search engines results
        self.seed_links = []

    def search(self):
        """
        Revise this method [NOT USED NOW]
        [TODO]: Will be better to use requests library for accessing to the nodes
        """
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/52.0.2743.82 Safari/537.36'}
        r = requests.get(self.url, self.payload, headers=headers)
        html = r.text
        self.html = html
        self.tree = lxml.html.fromstring(html)
        return self.get_urls(self.tree)

    def run(self):
        """
        Method for running different crawlers
        """
        if self.engine == 'google':
            return self.search_google()
        elif self.engine == 'google_cse':
            return self.search_google_cse()
        elif self.engine == 'google_blogs':
            return self.search_google_blogs()
        elif self.engine == 'google_scholar':
            return self.search_google_scholar()
        elif self.engine == 'google_news':
            return self.search_google_news()
        elif self.engine == 'bing':
            return self.search_bing()
        else:
            return self.search_yandex()

    def search_google(self):
        """
        This method uses Requests for querying google's search results page.
        It returns seed_links list for further crawling
        :return: seed_links list
        """
        for count in range(0, self.depth):
            # driver = webdriver.PhantomJS()
            url = self.engines_payload['google']['url'] + '?q=' + self.search_query + '&start=%s&sa=N' % self._google_cursor(count)
            r = requests.get(url)

            tree = lxml.html.fromstring(r.text)

            try:
                assert "Google" in tree.findtext('.//title')
            except AssertionError as e:
                logger.info("I can not find Google in page title")

            # Collect all result links for further crawling task
            hrefs = tree.xpath('//h3/a/@href')
            for href in hrefs:
                if href.startswith('/url?'):
                    clean_url = self._parse_google_href(href)
                    if clean_url is not None:
                        self.seed_links.append(clean_url)

        return self.seed_links

    def search_google_cse(self):
        """
        Another method for getting google's search results but from CSE (custom search engine):
        https://developers.google.com/custom-search/json-api/v1/using_rest.
        Using Requests library
        :return: seed_links list
        """

        # Check search depth value if it higher than 10
        # redefine it to display only 100 first results
        # see: https://developers.google.com/custom-search/json-api/v1/using_rest
        try:
            if self.depth > 10:
                raise MaxSearchDepthError
        except MaxSearchDepthError:
            logger.warn("Only the first 100 results will be displayed, due to CSE search depth limit.")
            self.depth = 10

        query = self.search_query

        cse_url = self.engines_payload['google_cse']['url']

        # We store options at JSONField. So we need to load them.
        options = json.loads(self.options) if self.options else None

        for count in range(0, self.depth):

            params = {
                'key': settings.GOOGLE_TRANSLATE_API_KEY,
                'cx': settings.CSE_ID,
                'q': query,
                'safe': 'medium',
                'start': self._google_cse_cursor(count),
            }

            if options:
                params.update(options)

            r = requests.get(cse_url, params=params)
            loaded_data = json.loads(r.text)

            if 'items' in loaded_data:
                for item in loaded_data['items']:
                    self.seed_links.append(item['link'])

        return self.seed_links

    def search_google_blogs(self):
        """
        Method for fetching results from google's blog search.
        Search query example: https://google.com/search?q=robotics+netherlands&tbm=nws&tbs=nrt:b&start=20
        tbm parameter responsible for NEWS search
        tbs parameter responsible for restriction search only from BLOGS
        start parameter responsible for results pagination
        :return: seed_links
        """
        for count in range(0, self.depth):
            url = self.engines_payload['google']['url'] + '?q=' + self.search_query + \
                  '&tbm=nws&tbs=nrt:b' + '&start=%s' % self._google_cursor(count)
            # For requesting Google patiently
            sleep(randint(1, 2))
            r = requests.get(url)

            tree = lxml.html.fromstring(r.text)

            try:
                assert "Google" in tree.findtext('.//title')
            except AssertionError as e:
                logger.info("I can't find Google in page title")

            # Collect all result links for further crawling task
            hrefs = tree.xpath('//h3/a/@href')
            for href in hrefs:
                if href.startswith('/url?'):
                    clean_url = self._parse_google_href(href)
                    if clean_url is not None:
                        self.seed_links.append(clean_url)

        return self.seed_links

    def search_google_scholar(self):
        """
        Method for fetching results from google's scholar.google.com.
        Search query example: https://scholar.google.com.ua/scholar?start=30&q=robotics+ai&start=30
        start parameter responsible for results pagination
        :return: seed_links
        """
        for count in range(0, self.depth):
            url = self.engines_payload['google_scholar']['url'] + '?q=' + self.search_query + \
                  '&start=%s' % self._google_cursor(count)
            # For requesting Google patiently
            sleep(randint(1, 2))
            r = requests.get(url)

            tree = lxml.html.fromstring(r.text)

            try:
                assert "Google" in tree.findtext('.//title')
            except AssertionError as e:
                logger.info("I can't find Google in page title")

            # Collect all result links for further crawling task
            hrefs = tree.xpath('//h3/a/@href')
            for href in hrefs:
                if href.startswith('/url?'):
                    clean_url = self._parse_google_href(href)
                    if clean_url is not None:
                        self.seed_links.append(clean_url)
                else:
                    self.seed_links.append(href)

        return self.seed_links

    def search_google_news(self):
        """
        Gets results from google's news.google.com and parses all them by feedparser
        Search query example: https://news.google.com/news/feeds?output=rss&q=banking&num=30.
        num parameter responsible for the number of returned entries (max=30, default=30)
        output parameter responsible for response format (ATOM or RSS)
        :return: seed_links
        """
        url = self.engines_payload['google_news']['url'] + '?q=' + self.search_query + '&output=rss&num=100'
        parser = RSSFeedParser(url)
        feed_links = parser.parse_rss()
        for link in feed_links:
            self.seed_links.append(self._parse_google_news_href(link))

        return self.seed_links

    def search_bing(self):
        """
        This method uses Requests for querying bing's search results.
        It returns seed_links list for further crawling
        :return: seed_links list
        """
        for count in range(0, self.depth):
            url = self.engines_payload['bing']['url'] + '?q=' + self.search_query + '&first=%s' % self._bing_cursor(count)
            r = requests.get(url)

            tree = lxml.html.fromstring(r.text)

            try:
                assert "Bing" in tree.findtext('.//title')
            except AssertionError as e:
                logger.info("I can't find Bing in page title")

            links = tree.xpath('//h2/a/@href')
            for link in links:
                self.seed_links.append(link)

        return self.seed_links

    def search_yandex(self):
        """
        This method uses Requests for querying yandex search results.
        It returns seed_links list for further crawling
        :return: seed_links list
        """
        for count in range(0, self.depth):
            url = self.engines_payload['yandex']['url'] + '?text=' + self.search_query + '&p=%s' % self._yandex_cursor(count)
            r = requests.get(url)

            tree = lxml.html.fromstring(r.text)

            # try:
            #     assert "Яндекс:" in tree.findtext('.//title')
            # except AssertionError as e:
            #     logger.info("I can't find Яндекс in page title")
            #     raise e

            links = tree.xpath('//h2/a/@href')
            for link in links:
                self.seed_links.append(link)

        return self.seed_links

    def get_urls(self, content):
        """
        Revise this method [NOT USED NOW]
        """
        print(content)
        np = self._next_page_path('google')
        print(np)
        return np

    def _next_page_path(self, engine):
        """
        Revise this method [NOT USED NOW]
        """
        if engine == 'google':
            return self.tree.xpath('*[contains(text(),"Next")]')[0].extract()

    def _google_cursor(self, counter):
        return counter * 10

    def _google_cse_cursor(self, counter):
        return counter * 10 + 1

    def _bing_cursor(self, counter):
        return 10 * counter + 1

    def _yandex_cursor(self, counter):
        return counter

    def _parse_google_href(self, href):
        """
        Revise this method
        """
        # Method for normalising Google's result link. Receives the link, parse it and gets the direct
        # url from querystring. E.g.: google's result links look's like:
        # https://www.google.com/url?q=some+query&url=http://foo.bar.url
        # so we should get only q parameter from google's querystring
        try:
            parsed = urlparse(href)
            url = parse_qs(parsed.query)['q'][0]
            return unquote(url)
        except KeyError:
            pass

    def _parse_google_news_href(self, href):
        """
        Revise this method
        """
        # Method for normalising Google News result link. Receives the link, parse it and gets the direct
        # url from querystring. E.g.: google's result links look's like:
        # https://www.news.google.com/url?q=some+query&url=http://foo.bar.url
        # so we should get only url parameter from google's querystring
        try:
            parsed = urlparse(href)
            url = parse_qs(parsed.query)['url'][0]
            return unquote(url)
        except KeyError:
            pass