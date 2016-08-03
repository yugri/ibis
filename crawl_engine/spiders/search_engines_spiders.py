from urllib.parse import quote

import io
from lxml import etree
import lxml.html
import requests


class SearchEngineParser(object):

    engines_payload = {
        'google': {'url': 'https://google.com/search', 'key': 'q'},
        'bing': {'url': 'https://www.bing.com/search', 'key': 'q'},
        'yandex': {'url': 'https://www.yandex.ua/search/', 'key': 'text'}
    }
    html = ''
    tree = ''

    def __init__(self, search_query, engine='google'):
        # Build query dict at init
        if engine == 'google' or 'yandex':
            search_query = "+".join(search_query.split())
        elif engine == 'yandex':
            search_query = quote(search_query)

        self.url = self.engines_payload[engine]['url']
        self.search_query = search_query
        self.payload = {
            self.engines_payload[engine]['key']: search_query
        }
        self.next_page_xpath = ''

    def search(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/52.0.2743.82 Safari/537.36'}
        r = requests.get(self.url, self.payload, headers=headers)
        html = r.text
        # f = io.StringIO(html)
        self.html = html
        self.tree = lxml.html.fromstring(html)
        v = ''
        return self.get_urls(self.tree)

    def get_urls(self, content):
        print(content)
        np = self._next_page_path('google')
        print(np)
        return lxml.html.fromstring(content)

    def _next_page_path(self, engine):

        if engine == 'google':
            return self.tree.xpath('//div[@class="navcnt"]')