import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from crawl_engine import tasks
from crawl_engine.models import Article
from crawl_engine.utils.translation_utils import separate
from celery import chord

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def run_translation_task(sender, instance, **kwargs):
    if not instance.translated:
        article_id = instance.id
        splitted_body = separate(instance.body)
        splitted_title = separate(instance.title)
        try:
            source = instance.source_language
            if not source:
                raise ValueError("Empty source_language field.")
        except ValueError:
            logger.info("The internal system can't detect article's language. "
                        "Trying to detect with Google Translate API.")
            source = tasks.detect_lang_by_google(splitted_body[0])
        logger.info("Detected language is: %s" % source)
        result_body = chord([tasks.google_translate.s(part, source) for part in splitted_body]) \
            (tasks.bound_and_save.s(article_id, source, 'body'))
        logger.info("Translation task for BODY has been queued, ID: %s" % result_body.id)
        result_title = chord([tasks.google_translate.s(part, source) for part in splitted_title]) \
            (tasks.bound_and_save.s(article_id, source, 'title'))
        logger.info("Translation task for TITLE has been queued, ID: %s" % result_title.id)