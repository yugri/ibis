import logging

from datetime import time, timedelta, date, datetime
from celery import shared_task, chain
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

from crawl_engine.models import SearchQuery, SearchTask
from crawl_engine.spiders.single_url_parser import ArticleParser
from crawl_engine.spiders.search_engines_spiders import SearchEngineParser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            # source='en',
            # target='de',
            # q=['Hi', 'Big HI']
        ).execute()
    except HttpError as e:
        logger.error(e)

    # data = json.loads(result)
    if result:
        from crawl_engine.models import Article
        article = Article.objects.get(pk=article_id)
        article.translated_title = result['translations'][0]['translatedText']
        article.translated_body = result['translations'][1]['translatedText']
        # Article language determines only on article's body text
        try:
            article.source_language = result['translations'][1]['detectedSourceLanguage']
        except KeyError:
            logger.info('Language already detected by internal system')
        finally:
            pass

        article.translated = True
        article.save()

    else:
        logger.info("Something wrong with received data")
        pass


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
    search_task = SearchTask()
    for search_query in search_queries:
        if search_query.active:
            if search_query.expired_period:
                task = chain(search_by_query.s(search_query.query, search_query.source, search_query.search_depth),
                             crawl_url.s(search_query.search_id))()
                search_query.last_processed = datetime.now()
                search_query.save()
                search_task.objects.create(task_id=task.id)
                search_task.save()


@shared_task
def search_by_query(query, engine, depth):
    parser = SearchEngineParser(query, engine, depth)
    return parser.run()