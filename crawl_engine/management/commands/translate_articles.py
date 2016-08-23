import logging

import itertools
from django.core.management.base import BaseCommand, CommandError
from crawl_engine.models import Article
from crawl_engine.tasks import detect_translate, bound_and_save
from crawl_engine.utils.sentence_tokenize import separate
from celery import group, chain, chord
from celery.contrib import rdb

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Translate all not translated articles'

    def handle(self, *args, **options):
        articles = Article.objects.filter(translated=False)

        for article in articles:
            article_id = article.id
            splitted_body = separate(article.body)
            source = article.source_language if article.source_language else None

            result = chord(detect_translate.s(part, source) for part in splitted_body)(bound_and_save.s(article_id))
            logger.debug("Task has been queued, ID: %s" % result.id)