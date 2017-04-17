import json
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from crawl_engine import tasks
from crawl_engine.models import Article, SearchQuery
from crawl_engine.tasks import run_job
from celery import chord

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def run_alchemy_task(sender, instance, **kwargs):
    if instance.translated and not instance.processed:
        instance.run_entities_collecting_task()


@receiver(post_save, sender=SearchQuery)
def crawl_email_search_links(sender, instance, created, **kwargs):
    """
    Additional processing for links in search type 'email'.(for quicker crawling links)
    In general workflow crawler process each search according to its period. For most searches its daily.
    1. When customer create new email search at ibis and save it, search is duplicated in crawler database and marked as
    non proceed.
    2. Customer receive an mailbox that he should use for registration for email subscription.
    (He also could send an email with links to that mailbox: to fill in the database with articles that he wants)
    3. At crawler side each 5 minutes task "check search queries" checks if any unproceed searches with uncrawled
    urls. After checking for new links, the search proceed date is updated and next time this task will return to the
    same search according to its period(next hour, or next day).
    4. But urls for email search could be updated during this day(or hour or week) and customer complaint that
    its too long to wait to see if articles were crawled or not.

    This code is additional to task 'check search queries'(for part that concerned email search and could be deleted
    without any warnings, so then email searches will be proceed as searches of all types(according to their period).

    """
    if instance.search_type == 'email':
        for value in instance.email_links.values():
            links = value.get('links', [])
            job = run_job.delay(links, instance.pk)
