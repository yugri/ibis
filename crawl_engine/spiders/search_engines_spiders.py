import logging
import json
import django

from django.conf import settings
import lxml.html
import requests
from urllib.parse import quote, parse_qs, urlparse, unquote

logger = logging.getLogger(__name__)


class SearchEngineParser(object):

    engines_payload = {
        'google': {
            'url': 'https://google.com/search',
            'key': 'q',
            'init_url': 'https://google.com'
        },
        'google_cse': {
            'url': 'https://www.googleapis.com/customsearch/v1',
            'key': 'q'
        },
        'bing': {'url': 'https://www.bing.com/search', 'key': 'q'},
        'yandex': {'url': 'https://www.yandex.ua/search/', 'key': 'text'}
    }
    html = ''
    tree = ''
    depth = 5  # The crawling depth

    def __init__(self, search_query, engine='google', depth=depth):
        # Build query dict at init
        if engine == 'google' or engine == 'yandex':
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
            return self.search_google_cse(50)
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
                logger.info("I can't find Google in page title")
                raise e

            # Collect all result links for further crawling task
            hrefs = tree.xpath('//h3/a/@href')
            for href in hrefs:
                if href.startswith('/url?'):
                    clean_url = self._parse_google_href(href)
                    if clean_url is not None:
                        self.seed_links.append(clean_url)

        return self.seed_links

    def search_google_cse(self, depth):
        """
        Another method for getting google's search results but from CSE (custom search engine):
        https://developers.google.com/custom-search/json-api/v1/using_rest.
        Using Requests library
        :return: seed_links list
        """

        query = self.search_query

        cse_url = self.engines_payload['google_cse']['url']

        for count in range(0, depth):

            params = {
                'key': settings.GOOGLE_TRANSLATE_API_KEY,
                'cx': settings.CSE_ID,
                'q': query,
                'safe': 'medium',
                'start': self._google_cse_cursor(count)
            }

            r = requests.get(cse_url, params=params)
            loaded_data = json.loads(r.text)

            for item in loaded_data['items']:
                self.seed_links.append(item['link'])

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
                raise e

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
        Revise this method [NOT USED NOW]
        """
        # Method for normalising Google's result link. Receives the link, parse it and gets the direct
        # url from querystring. E.g.: google's result links look's like:
        # https://www.google.com.ua/url?q=some=query&url=http://foo.bar.url
        # so we should get only url parameter from google's querystring
        # url = urlparse(link)
        try:
            parsed = urlparse(href)
            url = parse_qs(parsed.query)['q'][0]
            return unquote(url)
        except KeyError:
            pass