import json

from django.core.management import BaseCommand
from crawl_engine.tasks import upload_articles


class Command(BaseCommand):
    help = 'Upload all translate'

    def handle(self, *args, **options):
        return upload_articles()
