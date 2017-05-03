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

    def run(self):
        """
        Executes the regular url loading and parsing
        :return: article.id
        """
        result = None
        # Set our article DB model instance
        from crawl_engine.models import Article
        article = Article()

        # Try to load url and check if there is any other content type rather than html
        # If connections problems are take a place > handle request.ConnectionError and set r to None
        # We pass this response through all methods to avoid duplicate queries
        r = self._download_resource(self.url)

        if r is not None:
            # if PDF file
            if self._define_url_type(r) == '.pdf':
                article.article_url = self.url
                article.save(upload_file=True)
                article.search = SearchQuery.objects.get(pk=self.search) if self.search is not None else None
                result = article.id

            # else parse url by the Newspaper's library
            else:
                # Instantiate newspaper's Article api and download an article from given url
                page = np(self.url)
                page_loaded = False
                page_parsed = False
                try:
                    # Pass our response as 'r' argument
                    page = self._download_page(page, r)
                    page_loaded = True
                except TimeoutException as e:
                    logger.info(e)
                    result = e
                except ResponseCodeException as e:
                    logger.info("A resource responded with ERROR: %d" % e.status_code)
                    result = e.status_code
                try:
                    page.parse()
                    page_parsed = True
                except ArticleException as e:
                    logger.info(e)
                    result = e

                if page_loaded and page_parsed:

                    try:
                        author = extractArticleAuthor(page.html)
                    except (ValueError, OSError, KeyError):
                        # We pass all errors raised by a Newspaper module
                        # during getting all article's data
                        author = None
                    try:
                        title = extractArticleTitle(page.html)
                    except (ValueError, OSError, KeyError):
                        # We pass all errors raised by a Newspaper module
                        # during getting all article's data
                        title = None

                    text = page.text if page.text else extractArticleText(page.html)
                    # We should keep an articles html too for displaying it later
                    article_html = page.article_html if page.text else None
                    date = extractArticlePublishedDate(self.url, page.html)

                    if len(text) == 0:
                        result = "No body text in article."
                        return result
                    else:
                        article.article_url = page.url
                        article.title = title
                        article.top_image_url = page.top_image
                        try:
                            article.authors = author if author else article.authors[0]
                        except (IndexError, TypeError):
                            article.authors = ''

                        article.body = article_html if article_html else text
                        article.post_date_created = date

                        # Detect article source language at this point.
                        # If language is 'en' we save an <article.translated_title>
                        # and <article.translated_body> same as <title> and <body>.
                        title_lang = ''
                        text_lang = ''
                        try:
                            title_lang = detect(article.title)
                        except LangDetectException as e:
                            logger.error(e)
                            pass

                        try:
                            text_lang = detect(article.body)
                        except LangDetectException as e:
                            logger.error(e)
                            pass

                        if title_lang == 'en' and text_lang == 'en':
                            # Redefine articles body and translated_body to hold an
                            # article_html ONLY IF we deal with English language
                            article.body = article_html if article_html else text
                            article.translated_body = article_html if article_html else text
                            article.translated_title = title
                            article.translated = True

                        article.source_language = text_lang if text_lang == title_lang else None
                        search = SearchQuery.objects.get(pk=self.search) if self.search is not None else None
                        if search:
                            article.search = search
                            article.status, article.channel = article.article_status_from_search()
                        article.save(start_translation=not article.translated)
                        result = article.id
        else:
            result = "Some troubles with connection. Check Celery logs."
            # TODO: For now we don't RETRY. Should be implemented later
        return result

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
