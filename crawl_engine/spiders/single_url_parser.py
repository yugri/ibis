import logging
import requests
import re

from langdetect.lang_detect_exception import LangDetectException
from langdetect import detect
from lxml.html.clean import clean_html
from newspaper import Article as np
from newspaper import ArticleException
from readability.readability import Document

from crawl_engine.models import SearchQuery
from crawl_engine.models import Article

from crawl_engine.utils.articleAuthorExtractor import extractArticleAuthor
from crawl_engine.utils.articleDateExtractor import extractArticlePublishedDate
from crawl_engine.utils.articleTextExtractor import extractArticleTitle


logger = logging.getLogger(__name__)


class ArticleParser:
    """
    Single URL parser
    """
    def __init__(self, url, search=None):
        self.url = url
        self.search = search

    def _fallback_article_html(self, html):
        """ detect atricle html via Readbility library
        """
        try:
            return Document(html).summary(html_partial=True)
        except:
            return ''

    def run(self, save=True):
        """
        Save DEPRECATED param. If true saves Artivle and returns article id
        if false return unsaved article

        Executes the regular url loading and parsing
        :return: article.id
        """

        article = Article()

        # Try to load url and check if there is any other content type rather than html
        # If connections problems are take a place > handle request.ConnectionError and set r to None
        # We pass this response through all methods to avoid duplicate queries
        r = self._download_resource(self.url)

        if r is None:
            # TODO: For now we don't RETRY. Should be implemented later
            return "Some troubles with connection. Check Celery logs."

        # if PDF file
        if self._define_url_type(r) == '.pdf':
            article.article_url = self.url
            if not save:
                return article

            article.save(upload_file=True)
            return article.id

        # parse url by the Newspaper's library
        # Instantiate newspaper's Article api and download an article from given url
        page = np(self.url)

        try:
            # Pass our response as 'r' argument
            page = self._download_page(page, r)
            page.parse()
        except ArticleException as e:
            logger.info(e)
            return e

        try:
            author = extractArticleAuthor(page.html)
            article.authors = author if author else article.authors[0]
        except (ValueError, OSError, KeyError, IndexError, TypeError):
            # We pass all errors raised by a Newspaper module
            # during getting all article's data
            article.authors = ''

        try:
            article.title = extractArticleTitle(page.html)
        except (ValueError, OSError, KeyError):
            # We pass all errors raised by a Newspaper module
            # during getting all article's data
            pass

        article.article_url = page.url
        article.top_image_url = page.top_image
        article.post_date_created = extractArticlePublishedDate(self.url, page.html)

        body = page.article_html if page.article_html else self._fallback_article_html(page.html)
        # reduce number of chars and cleanup html
        article.body = re.sub("\s+", " ", clean_html(body))

        if len(article.body) == 0:
            return "No body text in article."

        # Detect article source language at this point.
        try:
            article.source_language = detect(article.body)
        except LangDetectException as e:
            logger.error(e)

        if article.source_language == 'en':
            # If language is 'en' we save an <article.translated_title>
            # and <article.translated_body> same as <title> and <body>.
            article.translated_body = article.body
            article.translated_title = article.title
            article.translated = True

        article.search = SearchQuery.objects.get(pk=self.search) if self.search is not None else None
        if not save:
            return article

        article.save(start_translation=not article.translated)
        return article.id

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

    def _download_page(self, page, response):
        """
        Method for downloading an article's page for further parsing by newspaper library
        @timeout decorator provides a TimeoutException when it occurs after defined time passed
        :param page:
        :return: page
        """
        try:
            # Newspaper Article handle html content from previous request
            # without new call
            page.download(html=response.text)
        except ArticleException as e:
            logger.info(e)
        return page

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

    def _define_url_type(self, response):
        content_type = response.headers.get('content-type')

        if 'application/pdf' in content_type:
            ext = '.pdf'
        elif 'text/html' in content_type:
            ext = '.html'
        else:
            ext = ''
            print('Unknown type: {}'.format(content_type))
        return ext
