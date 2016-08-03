from urllib.parse import quote
import lxml
import requests


class SearchEngineParser(object):

    engines_payload = {
        'google': {'url': 'https://google.com/search', 'key': 'q'},
        'bing': {'url': 'https://www.bing.com/search', 'key': 'q'},
        'yandex': {'url': 'https://www.yandex.ua/search/', 'key': 'text'}
    }

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

    def search(self):
        headers = {}
        r = requests.get(self.url, self.payload, headers=headers)