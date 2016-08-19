import logging

import itertools
from django.core.management.base import BaseCommand, CommandError
from crawl_engine.models import Article
from crawl_engine.tasks import detect_translate, bound_text, save_article
from crawl_engine.utils.sentence_tokenize import separate
from celery import group, chain, chord

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Translate all not translated articles'

    def handle(self, *args, **options):
        articles = Article.objects.filter(translated=False)

        for article in articles:
            article_id = article.id
            splitted_title = separate(article.body)
            source = article.source_language if article.source_language else None
            result = chain(bound_text.apply_async(splitted_title), save_article(article_id))
            print(result)