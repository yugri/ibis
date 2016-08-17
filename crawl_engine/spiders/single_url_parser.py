import re
import logging
from langdetect.lang_detect_exception import LangDetectException
from newspaper import Article as np
from crawl_engine.utils.articleAuthorExtractor import extractArticleAuthor
from crawl_engine.utils.articleDateExtractor import extractArticlePublishedDate
from crawl_engine.utils.articleTextExtractor import extractArticleText, extractArticleTitle
from langdetect import detect

logger = logging.getLogger(__name__)


class EmptyBodyException(Exception):
    pass


class ArticleParser:

    def __init__(self, url, search_id):
        self.url = url
        self.search_id = search_id

    def run(self):
        # Instantiate newspaper's Article api
        page = np(self.url)
        page.download()
        page.parse()

        author = extractArticleAuthor(page.html)
        title = extractArticleTitle(page.html)

        text = page.text if page.text else extractArticleText(page.html)
        date = extractArticlePublishedDate(self.url, page.html)

        try:
            if len(text) == 0:
                raise EmptyBodyException("No body text in article.")
        except EmptyBodyException as e:
            exit(str(e))

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

        article.source_language = text_lang if text_lang == title_lang else None
        article.search_id = self.search_id
        article.save()

        return article.id

    def download_image(self, article_instance):
        article_url = self.url
        page = np(self.url)
        page.download()
        page.parse()
        article_instance.top_image_url = page.top_image
        article_instance.save()





