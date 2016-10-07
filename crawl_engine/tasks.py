import json
import logging
import os
import redis

from datetime import datetime
from pybloomfilter import BloomFilter
from time import sleep
from random import randint

import requests
from celery import shared_task, chain, group
from celery.schedules import crontab
from celery.exceptions import MaxRetriesExceededError
from celery.task import periodic_task
from django.conf import settings
from django.utils.timezone import utc
from django.forms.models import model_to_dict

from crawl_engine.models import Article, SearchQuery, SearchTask
from crawl_engine.serializers import ArticleTransferSerializer
from crawl_engine.spiders.single_url_parser import ArticleParser
from crawl_engine.spiders.search_engines_spiders import SearchEngineParser
from crawl_engine.spiders.rss_spider import RSSFeedParser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from requests.exceptions import HTTPError

from crawl_engine.utils.ibis_client import IbisClient, chunks

logger = logging.getLogger(__name__)


@shared_task(name='crawl_engine.tasks.crawl_url')
def crawl_url(url, search=None):
    result = None
    try:
        article = Article.objects.filter(article_url=url)
        result = "Url was already crawled"
    except Article.DoesNotExist:
        parser = ArticleParser(url, search)
        result = parser.run()

    return result


@shared_task(name='crawl_engine.tasks.translate_content')
def translate_content(article_title, article_body, article_id, source_language):
    service = build('translate', 'v2',
                    developerKey=settings.GOOGLE_TRANSLATE_API_KEY)
    result = None
    try:
        result = service.translations().list(
            source=source_language if source_language else None,
            target='en',
            q=[article_title, article_body]
        ).execute()
    except HttpError as e:
        logger.error(e)

    # data = json.loads(result)
    if result:
        # from crawl_engine.models import Article
        article = Article.objects.get(pk=article_id)
        article.translated_title = result['translations'][0]['translatedText']
        article.translated_body = result['translations'][1]['translatedText']
        # Article language determines only on article's body text
        try:
            article.source_language = result['translations'][1]['detectedSourceLanguage']
        except KeyError:
            logger.info('Language already detected by internal system')
        except IndexError:
            logger.info('Seems like the language is already set for this article')
        finally:
            pass

        article.translated = True
        article.save(start_translation=False)

    else:
        logger.info("Something wrong with received data")
        pass


@shared_task(name='crawl_engine.tasks.google_translate')
def google_translate(text, source):
    """
    Method implements only translation mechanism
    :param text: str
    :param source: str
    :return translated_text
    """
    service = build('translate', 'v2',
                    developerKey=settings.GOOGLE_TRANSLATE_API_KEY)
    result = None
    sleep(randint(1, 2))
    try:
        result = service.translations().list(
            source=source,
            target='en',
            q=text
        ).execute()
    except HttpError as e:
        logger.error(e)

    try:
        translated_text = result['translations'][0]['translatedText']
    except KeyError:
        logger.info("Google API didn't detect a language.")
        translated_text = ''
    except TypeError:
        translated_text = ''
    finally:
        pass
    return translated_text


@shared_task(name='crawl_engine.tasks.google_detect_translate')
def google_detect_translate(text, source=None):
    """
    Method implements both detection (if source is not provided)
    and translation mechanisms
    :param text: str
    :param source: str
    :return translated_text, detected_lang: str, str
    """
    service = build('translate', 'v2',
                    developerKey=settings.GOOGLE_TRANSLATE_API_KEY)
    result = None
    translated_text = ''
    detected_lang = ''

    # Sleep for a while. Google has limitations for querying,
    # see: https://cloud.google.com/translate/v2/pricing
    sleep(randint(1, 2))
    try:
        result = service.translations().list(
            source=source,
            target='en',
            q=text
        ).execute()
    except HttpError as e:
        logger.error(e)
    if result:
        try:
            translated_text = result['translations'][0]['translatedText']
        except KeyError:
            logger.info("Google Translate API cant't translate the text.")
        finally:
            pass
        try:
            detected_lang = result['translations'][0]['detectedSourceLanguage']
        except KeyError:
            logger.info('Language already detected by internal system.')
        finally:
            pass
    return translated_text, detected_lang


@shared_task(name='crawl_engine.tasks.detect_lang_by_google')
def detect_lang_by_google(text):
    """
    Method implements detection mechanism. Returns language from supported,
    see: https://cloud.google.com/translate/v2/discovering-supported-languages-with-rest
    :param text: str
    :return detected_lang: str
    """
    service = build('translate', 'v2',
                    developerKey=settings.GOOGLE_TRANSLATE_API_KEY)
    result = None
    lang = ''

    # Sleep for a while. Google has limitations for querying,
    # see: https://cloud.google.com/translate/v2/pricing

    sleep(randint(1, 2))
    try:
        result = service.detections().list(
            q=text
        ).execute()
    except HttpError as e:
        logger.error(e)
    try:
        lang = result['detections'][0][0]['language']
    except KeyError:
        logger.info("Google API didn't detect a language.")
        lang = ''
    finally:
        pass
    return lang


@shared_task(name='crawl_engine.tasks.bound_and_save')
def bound_and_save(text_parts, article_id, source, destination):
    """
    Called after detect_translate task and bound all translated parts together
    and save an article
    :param text_parts: list
    :param article_id: int
    :param source: str
    :param destination: str
    """
    text = ''.join(text_parts)
    article = Article.objects.get(pk=article_id)
    logger.info("Fetched an article instance from DB, ID: %s" % article.id)
    article.source_language = source
    if destination == 'body':
        article.translated_body = text
    elif destination == 'title':
        article.translated_title = text
    # Only if translated_body is present an article sets to translated and processed
    # before being pushed to IBIS
    if article.translated_body:
        article.translated = True
        article.processed = True
    article.save()


@periodic_task(
    run_every=(crontab(minute='*/5')),
    name="crawl_engine.tasks.check_search_queries",
    ignore_result=True
)
def check_search_queries():
    """
    This task should get all SearchQuery objects and check if there is an active.
    If so the periodic task (depends on search_type) should be presented at schedule. In other case the task <___>
    should be removed from schedule
    """
    result = "All queries were checked"
    search_queries = SearchQuery.objects.all()
    job_id = None
    for search_query in search_queries:
        if search_query.active:
            if search_query.expired_period:
                # We need to check search_type at this point
                # and initiate different tasks if any
                if search_query.search_type == 'search_engine' or search_query.search_type == 'simple_search':
                    job = chain(search_by_query.s(search_query.query, search_query.source, search_query.search_depth,
                                                  search_query.options),
                                run_job.s(search_query.pk))()
                    job_id = job.id
                elif search_query.search_type == 'rss':
                    job = chain(read_rss.s(search_query.rss_link), run_job.s(search_query.pk))()
                    job_id = job.id
                elif search_query.search_type == 'article':
                    job = run_job.delay([search_query.article_url], search_query.pk)
                    job_id = job.id
                # Update search last processed date, save it and create the task obj
                now = datetime.utcnow().replace(tzinfo=utc)
                search_query.last_processed = now
                search_query.save()
                # SearchTask.objects.create(task_id=job_id, search_query=search_query)
    return result


@shared_task(name='crawl_engine.tasks.search_by_query')
def search_by_query(query, engine, depth, options):
    parser = SearchEngineParser(query, engine, depth, options)
    return parser.run()


@shared_task(name='crawl_engine.tasks.read_rss')
def read_rss(rss_link):
    reader = RSSFeedParser(rss_link)
    return reader.parse_rss()


@shared_task(name='crawl_engine.tasks.run_job')
def run_job(url_list, search=None):
    tasks = []
    try:
        for url in url_list:
            tasks.append(crawl_url.s(url, search))

    except IndexError:
        pass

    job = group(tasks)
    result = job.apply_async()
    return result.id


@periodic_task(
    run_every=(crontab(minute='*/2')),
    name="crawl_engine.tasks.upload_articles",
    ignore_result=True,
    bind=True
)
def upload_articles(self, test=False):
    """
    This task checks filters NON processed articles from DB and pushes them to IBIS system
    :return: nothing
    """
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    task = r.get('crawl_engine.tasks.upload_articles')
    if task:
        pass
    else:
        r.set('crawl_engine.tasks.upload_articles', 1)
        if test:
            articles = Article.objects.filter(translated=True, processed=True, pushed=False)[:5]
        else:
            articles = Article.objects.filter(
                translated=True,
                processed=True,
                pushed=False,
                post_date_crawled__gte=datetime(2016, 10, 4).replace(tzinfo=utc),
                search__search_id__isnull=False
            ).order_by('-post_date_crawled')
        if articles.count() > 0:
            for article_chunk in chunks(articles, 50):
                data = ArticleTransferSerializer(article_chunk, many=True).data
                client = IbisClient()
                payload = json.dumps(data)
                result = client.push_articles(data=payload)
                if result.status_code == 201:
                    for article in article_chunk:
                        article.pushed = True
                        article.save()
                    return 'Successfully Created'
                if result.status_code == 400:
                    print(result.text)
                    try:
                        upload_articles.retry(countdown=5, max_retries=3)
                    except MaxRetriesExceededError as e:
                        print(e)
                if result.status_code == 500:
                    print(result.text)
                    try:
                        upload_articles.retry(countdown=5, max_retries=3)
                    except MaxRetriesExceededError as e:
                        print(e)
    r.delete(self.name)