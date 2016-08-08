import logging
import io
from lxml import etree
import lxml.html
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote, parse_qs, urlparse


logger = logging.getLogger(__name__)


class SearchEngineParser(object):

    engines_payload = {
        'google': {
            'url': 'https://google.com/search',
            'key': 'q',
            'init_url': 'https://google.com'
        },
        'bing': {'url': 'https://www.bing.com/search', 'key': 'q'},
        'yandex': {'url': 'https://www.yandex.ua/search/', 'key': 'text'}
    }
    html = ''
    tree = ''
    depth = 1  # The crawling depth

    def __init__(self, search_query, engine='google', depth=1):
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
        self.depth = depth
        self.next_page_xpath = ''

        # Seed links fetched from search engines results
        self.seed_links = []

    def search(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/52.0.2743.82 Safari/537.36'}
        r = requests.get(self.url, self.payload, headers=headers)
        html = r.text
        self.html = html
        self.tree = lxml.html.fromstring(html)
        return self.get_urls(self.tree)

    def search_google(self):

        # This method uses selenium with PhantomJS headless webdriver
        # only for crawl google search results.
        # It returns seed_links list for further crawling

        for count in range(0, self.depth):
            driver = webdriver.PhantomJS()
            url = self.engines_payload['google']['url'] + '?q=' + self.search_query + '&start=%s&sa=N' % self._google_cursor(count)
            driver.get(url)

            try:
                assert "Google" in driver.title
            except AssertionError as e:
                logger.info("I can't find Google in drivers title")
                raise e

            try:
                dynamic_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.LINK_TEXT, 'Уперед' or 'Next'))
                    # EC.visibility_of_element_located((By.ID, "pnnext"))
                )
            except BaseException as e:
                raise e
            tree = lxml.html.fromstring(driver.page_source)

            # Collect all result links for further crawling task
            links = driver.find_elements_by_xpath('//h3/a')
            for link in links:
                self.seed_links.append(link.get_attribute('href'))

            next_url = dynamic_element.get_attribute('href')
            if next_url:
                self.search_query = next_url

        return self.seed_links

    def get_urls(self, content):
        print(content)
        np = self._next_page_path('google')
        print(np)
        return np

    def _next_page_path(self, engine):

        if engine == 'google':
            return self.tree.xpath('*[contains(text(),"Next")]')[0].extract()

    def _google_cursor(self, counter):
        return counter * 10

    def _parse_google_link(self, link):
        # Method for normalising Google's result link. Receives the link, parse it and gets the direct
        # url from querystring. E.g.: google's result links look's like:
        # https://www.google.com.ua/url?q=some=query&url=http://foo.bar.url
        # so we should get only url parameter from google's querystring
        url = urlparse(link)
        return parse_qs(url.query)['url'][0]