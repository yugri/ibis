import logging
from django.core.management.base import BaseCommand
from langdetect import detect
from langdetect.detector import LangDetectException

from crawl_engine.models import Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Guess and set language for all articles'

    def handle(self, *args, **options):
        articles = Article.objects.all()
        for article in articles:
            title_lang = ''
            body_lang = ''
            try:
                title_lang = detect(article.title)
            except LangDetectException as e:
                logger.error(e)
                pass

            try:
                body_lang = detect(article.body)
            except LangDetectException as e:
                logger.error(e)
                pass

            if title_lang == 'en' and body_lang == 'en':
                article.translated_title = article.title
                article.translated_body = article.body
                article.translated = True

            article.source_language = body_lang if body_lang == title_lang else ''
            article.save()

        logger.info('Language detection completed')
