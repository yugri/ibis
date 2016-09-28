import logging
from django.core.management.base import BaseCommand
from crawl_engine.tasks import run_job

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reads ../..urls.txt file and schedule to crawl all links from his file.'

    def handle(self, *args, **options):
        urls_list = open('../..urls.txt', 'r').readlines()
        job = run_job.apply_async((urls_list, None))

        logger.info('Crawl job started %s' % job.id)