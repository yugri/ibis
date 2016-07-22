import logging
from django.core.management.base import BaseCommand, CommandError
from crawl_engine.models import Article
from crawl_engine.tasks import translate_content

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Translate all not translated articles'

    def handle(self, *args, **options):
        articles = Article.objects.filter(translated=False)

        for article in articles:
            result = translate_content.apply_async((
                article.title,
                article.body,
                article.id,
                article.source_language
            ), countdown=10)
        logger.info('Translation tasks are already in queue')