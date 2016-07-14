from django.conf import settings
from celery import shared_task
from crawl_engine.spiders.single_url_parser import ArticleParser
import requests, bs4


@shared_task
def crawl_url(url, issue_id):

    parser = ArticleParser(url, issue_id)
    result = parser.run()

    return result