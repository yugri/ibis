import re
import logging

import sys
from celery import chord
from langdetect.lang_detect_exception import LangDetectException
from newspaper import Article as np

from crawl_engine.tasks import google_translate, bound_and_save, detect_lang_by_google
from crawl_engine.models import SearchQuery
from crawl_engine.utils.articleAuthorExtractor import extractArticleAuthor
from crawl_engine.utils.articleDateExtractor import extractArticlePublishedDate
from crawl_engine.utils.articleTextExtractor import extractArticleText, extractArticleTitle
from langdetect import detect

from crawl_engine.utils.translation_utils import separate

logger = logging.getLogger(__name__)


class EmptyBodyException(Exception):
    pass


class ArticleParser:

    def __init__(self, url, search):
        self.url = url
        self.search = search

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
        article.search = SearchQuery.objects.get(pk=self.search)
        article.save()

        # Execute the translation task now
        self.run_translation_task(article)

        return article.id

    def download_image(self, article_instance):
        article_url = self.url
        page = np(self.url)
        page.download()
        page.parse()
        article_instance.top_image_url = page.top_image
        article_instance.save()

    def run_translation_task(self, instance):
        if not instance.translated:
            article_id = instance.id
            splitted_body = separate(instance.body)
            splitted_title = separate(instance.title)
            try:
                source = instance.source_language
                if not source:
                    raise ValueError("Empty source_language field.")
            except ValueError:
                logger.info("The internal system can't detect article's language. "
                            "Trying to detect with Google Translate API.")
                source = detect_lang_by_google(splitted_body[0])
            logger.info("Detected language is: %s" % source)

            # Check if detected language is English. If YES we store the
            # translated_title and translated_body the same title and body
            if source == "en":
                instance.translated_title = instance.title
                instance.translated_body = instance.body
                instance.save()
                logger.info("No need to execute the translation task because article's language is EN.")
            # Else run translation tasks. Tasks will run separately for the body and the title.
            else:
                result_body = chord([google_translate.s(part, source) for part in splitted_body]) \
                    (bound_and_save.s(article_id, source, 'body'))
                logger.info("Translation task for BODY has been queued, ID: %s" % result_body.id)
                result_title = chord([google_translate.s(part, source) for part in splitted_title]) \
                    (bound_and_save.s(article_id, source, 'title'))
                logger.info("Translation task for TITLE has been queued, ID: %s" % result_title.id)





