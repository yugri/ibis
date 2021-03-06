import logging

from django.core.management import BaseCommand
from django.db.models import Count
from crawl_engine.models import Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deletes all article objects duplicates from given database'

    def handle(self, *args, **options):
        duplicate_articles = Article.objects.values('article_url').annotate(
            url_count=Count('article_url')
        ).filter(url_count__gt=1)
        for article in duplicate_articles:
            arts = Article.objects.filter(article_url=article['article_url'])[1:]
            for a in arts:
                a_id = a.id
                a.delete()
                self.stdout.write(self.style.SUCCESS('Article duplicate %s DELETED' % a_id))
