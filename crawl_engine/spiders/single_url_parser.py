import logging
import requests
import re
from readability import readability

from langdetect.lang_detect_exception import LangDetectException
from langdetect import detect
from lxml.html.clean import clean_html
from newspaper import Article as np
from newspaper import ArticleException


from crawl_engine.models import SearchQuery
from crawl_engine.models import Article

from crawl_engine.utils.articleAuthorExtractor import extractArticleAuthor
from crawl_engine.utils.articleDateExtractor import extractArticlePublishedDate


logger = logging.getLogger(__name__)


class ArticleParser:
    """
    Single URL parser
    """
    def __init__(self, url, search=None):
        self.url = url
        self.search = search

    def setattr(self, attr, value):
        """ Update attribiute only if new present """
        if value is None or value == '':
            return

        setattr(self.article, attr, value)

    def setattrs(self, dic):
        for attr, value in dic.items():
            self.setattr(attr, value)

    def parse_binary(self):
        self.article.status = 'trash'

    def parse_html(self, response):
        # fix request encoding issue (should test it carefully)
        FAIL_ENCODING = 'ISO-8859-1'
        html = response.text if response.encoding != FAIL_ENCODING else response.content

        # try readability parser
        try:
            document = readability.Document(html)
            self.setattr('title', document.short_title())
            self.setattr('body', document.summary(html_partial=True))
        except:
            pass

        # try the Newspaper's parser
        try:
            page = np(self.article.article_url)
            page.download(html=html)
            page.parse()
        except ArticleException as e:
            logger.info(e)
            pass

        self.setattr('body', page.article_html)
        self.setattr('authors', ', '.join(page.authors))
        self.setattr('top_image_url', page.top_image)

        # the most preferable way is custom parsers
        self.setattr('authors', extractArticleAuthor(html))
        self.setattr('post_date_created', extractArticlePublishedDate(self.article.article_url, html))

    def run(self, save=True, initial={}):
        """
        Save DEPRECATED param. If true saves Artivle and returns article id
        if false return unsaved article

        Executes the regular url loading and parsing
        :return: article.id
        """

        self.article = Article()

        # we start from less trusted methods and rewrite attributes
        # by more trusted resources
        self.setattrs(initial)

        # Try to load url and check if there is any other content type rather than html
        r = self._download_resource(self.url)

        if r is None:
            # TODO: For now we don't RETRY. Should be implemented later
            return "Some troubles with connection. Check Celery logs."

        self.setattr('article_url', r.url)

        # if not html
        if 'html' not in r.headers.get('content-type', '').lower():
            self.parse_binary()
        else:
            self.parse_html(r)

        # reduce number of chars and cleanup html
        self.article.body = re.sub("\s+", " ", clean_html(self.article.body))

        if len(self.article.body) == 0:
            return "No body text in article."

        # Detect article source language at this point.
        try:
            self.article.source_language = detect(self.article.body)
        except LangDetectException as e:
            logger.error(e)

        if self.article.source_language == 'en':
            # If language is 'en' we save an <article.translated_title>
            # and <article.translated_body> same as <title> and <body>.
            self.article.translated_body = self.article.body
            self.article.translated_title = self.article.title
            self.article.translated = True

        self.article.search = SearchQuery.objects.filter(pk=self.search).first()
        if not save:
            return self.article

        self.article.save(start_translation=not self.article.translated)
        return self.article.id

    def download_image(self, article_instance):
        """
        Executes a new request for the article by it's url,
        gets a top image and saves it.
        :param article_instance:
        :return: nothing
        """
        page = np(self.url)
        page.download()
        page.parse()
        article_instance.top_image_url = page.top_image
        article_instance.save(start_translation=False)

    def _download_resource(self, url):
        """
        Method for requesting resource with Requests
        :param url:
        :return: response
        """

        try:
            response = requests.get(url, timeout=7)
            response.raise_for_status()

            return response
        except requests.exceptions.HTTPError as e:
            logger.info("Failed loading [%s] - %s" % (url, e))
        except requests.exceptions.Timeout:
            logger.info("Page loading [%s] takes to long. Retry later." % url)

        return None
