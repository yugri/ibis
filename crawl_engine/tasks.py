from django.conf import settings
from crawl_engine.models import Article
from celery import shared_task
import requests, bs4


@shared_task
def crawl_url(url, issue_id):
    r = requests.get(url)
    text = r.text

    article = Article(article_url=url, title="Some title", body="Big body")
    article.save()

    return article


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)