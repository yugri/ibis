import logging

from django.core.management import BaseCommand
from django.db.models import Count
from crawl_engine.models import Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deletes all article objects duplicates'

    def add_arguments(self, parser):
        parser.add_argument('db_name', type=str)

    def handle(self, *args, **options):
        database = options['db_name']
        duplicate_articles = Article.objects.using(database).values('article_url').annotate(
            url_count=Count('article_url')
        ).filter(url_count__gt=1)
        for article in duplicate_articles:
            a = Article.objects.using('articles').filter(article_url=article['article_url'])[0]
            a_id = a.id
            a.delete()
            self.stdout.write(self.style.SUCCESS('Article duplicate %s DELETED' % a_id))