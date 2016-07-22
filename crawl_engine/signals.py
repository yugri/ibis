import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from crawl_engine.tasks import translate_content

from crawl_engine.models import Article

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def article_post_save(sender, instance, **kwargs):

    if not instance.translated:
        if not instance.translated_title or not instance.translated_body:
            # Initiate the translation task at this point if needed
            translate_content.apply_async((instance.title,
                instance.body, instance.id, instance.source_language), countdown=10)
    else:
        logger.info("An article is already translated.")
        return None