import logging
from django.core.management.base import BaseCommand
from crawl_engine.spiders.single_url_parser import ArticleParser

from crawl_engine.models import Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Download images from given article node'

    def handle(self, *args, **options):
        articles = Article.objects.all()
        for article in articles:
            parser = ArticleParser(article.article_url, None)
            parser.download_image(article)
