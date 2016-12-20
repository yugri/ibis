import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from crawl_engine import tasks
from crawl_engine.models import Article
from celery import chord

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def run_alchemy_task(sender, instance, **kwargs):
    if instance.translated:
        instance.run_entities_collecting_task()
