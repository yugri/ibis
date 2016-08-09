import logging
from celery import shared_task
from django.conf import settings

from crawl_engine.spiders.single_url_parser import ArticleParser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


@shared_task
def crawl_url(url, issue_id):

    parser = ArticleParser(url, issue_id)
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