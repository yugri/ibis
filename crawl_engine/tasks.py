import logging

from datetime import time, timedelta, date, datetime
from time import sleep

from celery import shared_task, chain, task, group
from celery.schedules import crontab
from celery.task import periodic_task
from celery.contrib import rdb
from django.conf import settings
from django.utils.timezone import utc

from crawl_engine.models import SearchQuery, SearchTask
from crawl_engine.spiders.single_url_parser import ArticleParser
from crawl_engine.spiders.search_engines_spiders import SearchEngineParser
from crawl_engine.utils.sentence_tokenize import separate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from crawl_engine.models import Article

logger = logging.getLogger(__name__)


@shared_task
def crawl_url(url, search_id):

    parser = ArticleParser(url, search_id)
    result = parser.run()

    return result


@shared_task
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
        article.save()

    else:
        logger.info("Something wrong with received data")
        pass


@shared_task
def detect_translate(text, source=None):
    """
    Method implements both detection amd translation mechanisms
    :param text: str
    :param source: str
    :return translated_text, detected_lang: str, str
    """
    service = build('translate', 'v2',
                    developerKey=settings.GOOGLE_TRANSLATE_API_KEY)
    result = None
    translated_text = None
    detected_lang = None

    # Sleep for a while. Google has limitations for querying,
    # see: https://cloud.google.com/translate/v2/pricing
    sleep(2)
    try:
        result = service.translations().list(
            source=source,
            target='en',
            q=[text]
        ).execute()
    except HttpError as e:
        logger.error(e)
    if result:
        translated_text = result['translations'][0]['translatedText']
        try:
            detected_lang = result['translations'][0]['detectedSourceLanguage']
        except KeyError:
            logger.info('Language already detected by internal system')
        finally:
            pass
    return translated_text, detected_lang


@shared_task
def bound_and_save(parts, article_id):
    """
    Called after detect_translate task and bound all translated parts together
    :param parts: list
    :return text: str
    """
    text = ''.join(parts)
    article = Article.objects.get(pk=article_id)
    article.title = text
    article.save()


@shared_task
def translate_part(part, lang):
    service = build('translate', 'v2',
                    developerKey=settings.GOOGLE_TRANSLATE_API_KEY)
    result = None
    try:
        result = service.translations().list(
            source=lang,
            target='en',
            q=[part]
        ).execute()
    except HttpError as e:
        logger.error(e)

    if result:
        translated_part = result['translations'][0]['translatedText']
        # try:
        #     detected_language = result['translations'][1]['detectedSourceLanguage']
        # except KeyError:
        #     logger.info('Language already detected by internal system')
        # except IndexError:
        #     logger.info('Seems like the language is already set for this article')
        # finally:
        #     pass


@periodic_task(
    run_every=(crontab(minute='*/5')),
    name="check_search_queries",
    ignore_result=True
)
def check_search_queries():
    """
    This task should get all SearchQuery objects and check if there is an active.
    If so the periodic task <___> should be presented at schedule. In other case the task <___>
    should be removed from schedule
    """
    search_queries = SearchQuery.objects.all()
    for search_query in search_queries:
        if search_query.active:
            if search_query.expired_period:
                job = chain(search_by_query.s(search_query.query, search_query.source, search_query.search_depth),
                            run_job.s(search_query.search_id))()
                now = datetime.utcnow().replace(tzinfo=utc)
                search_query.last_processed = now
                search_query.save()
                SearchTask.objects.create(task_id=job.id, search_query=search_query)


@shared_task
def search_by_query(query, engine, depth):
    parser = SearchEngineParser(query, engine, depth)
    return parser.run()


@shared_task
def run_job(url_list, search_id):
    tasks = []
    try:
        for url in url_list:
            tasks.append(crawl_url.s(url, search_id))

    except IndexError:
        pass

    job = group(tasks)
    result = job.apply_async()
    return result.id