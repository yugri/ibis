import re
import logging

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


class EmptyBodyException(Exception):
    pass


class ArticleParser:
    """
    Single URL parser
    """
    def __init__(self, url, url_filter, search=None):
        self.url = url
        self.search = search
        self.filter = url_filter

    def run(self):
        """
        :return: article.id
        """
        # Instantiate newspaper's Article api
        page = np(self.url)
        page_loaded = False
        page_parsed = False
        try:
            page = self._download_page(page)
            page_loaded = True
        except TimeoutException as e:
            logger.info(e)
        try:
            page.parse()
            page_parsed = True
        except ArticleException as e:
            logger.info(e)

        if page_loaded and page_parsed:

            author = extractArticleAuthor(page.html)
            title = extractArticleTitle(page.html)

            text = page.text if page.text else extractArticleText(page.html)
            date = extractArticlePublishedDate(self.url, page.html)

            if len(text) == 0:
                result = "No body text in article."
                return result
            else:

                # Set our article DB model instance
                from crawl_engine.models import Article
                article = Article()

                article.article_url = page.url
                article.title = title
                article.top_image_url = page.top_image
                try:
                    article.authors = author if author else article.authors[0]
                except IndexError:
                    article.authors = ''

                article.body = re.sub('\n+', '\n', re.sub(' +', ' ', text))
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
                    article.translated_title = title
                    article.translated_body = text
                    article.translated = True
                    article.processed = True

                article.source_language = text_lang if text_lang == title_lang else None
                article.search = SearchQuery.objects.get(pk=self.search) if self.search is not None else None
                # Add our URL to Bloom Filter
                self.filter.add(page.url)
                article.save(start_translation=not article.translated)
                result = article.id
            return result

    def download_image(self, article_instance):
        """
        Executes a new request for the article by it's url,
        gets a top image and saves it.
        :param article_instance:
        :return: nothing
        """
        article_url = self.url
        page = np(self.url)
        page.download()
        page.parse()
        article_instance.top_image_url = page.top_image
        article_instance.save(start_translation=False)

    @timeout(5)
    def _download_page(self, page):
        try:
            page.download()
        except ArticleException as e:
            logger.info(e)
        return page
