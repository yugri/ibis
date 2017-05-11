import logging

import requests
from langdetect.lang_detect_exception import LangDetectException
from newspaper import Article as np
from newspaper import ArticleException

from crawl_engine.models import SearchQuery
from crawl_engine.utils.articleAuthorExtractor import extractArticleAuthor
from crawl_engine.utils.articleDateExtractor import extractArticlePublishedDate
from crawl_engine.utils.articleTextExtractor import extractArticleText, extractArticleTitle
from crawl_engine.utils.timeout import timeout, TimeoutException
from langdetect import detect
from readability.readability import Document

logger = logging.getLogger(__name__)


RESPONSE_ERROR_CODES = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                        421, 422, 423, 424, 426, 428, 429, 431, 451, 500, 501, 502, 503, 504, 505, 506, 507, 508, 510,
                        511]


class EmptyBodyException(Exception):
    pass


class ResponseCodeException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
    pass


class ArticleParser:
    """
    Single URL parser
    """
    def __init__(self, url, search=None):
        self.url = url
        self.search = search

    def _fallback_article_html(delf, html):
        """ detect atricle html via Readbility library
        """
        try:
            return Document(html).content()
        except:
            return ''

    def run(self):
        """
        Executes the regular url loading and parsing
        :return: article.id
        """

        # Set our article DB model instance
        from crawl_engine.models import Article
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
            article.save(upload_file=True)
            return article.id

        # parse url by the Newspaper's library
        # Instantiate newspaper's Article api and download an article from given url
        page = np(self.url)

        try:
            # Pass our response as 'r' argument
            page = self._download_page(page, r)
            page.parse()
        except TimeoutException as e:
            logger.info(e)
            return e
        except ResponseCodeException as e:
            logger.info("A resource responded with ERROR: %d" % e.status_code)
            return e.status_code
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

        article.body = page.article_html if page.article_html else self._fallback_article_html(page.html)
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

    @timeout(5)
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

    @timeout(7)
    def _download_resource(self, url):
        """
        Method for requesting resource with Requests
        @timeout decorator provides a TimeoutException when it occurs after defined time passed
        :param url:
        :return: response
        """
        try:
            response = requests.get(url)
            # Check response status code for errors
            if response.status_code in RESPONSE_ERROR_CODES:
                ex = ResponseCodeException(status_code=response.status_code)
                raise ex
        except TimeoutException:
            logger.info("Page loading [%s] takes to long. Retry later." % url)
            response = None
        return response

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
