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
def translate_content(article_title, article_body, article_id, source_language=''):
    service = build('translate', 'v2',
                    developerKey=settings.GOOGLE_TRANSLATE_API_KEY)
    result = None
    try:
        result = service.translations().list(
            # source=source_language,
            # target='en',
            # q=[article_title, article_body]
            source='en',
            target='de',
            q=['Hi', 'Big HI']
        ).execute()
    except HttpError as e:
        logger.error(e)

    # if type(result) == 'json':
    #     data = json.loads(result)
    # else:
    #     raise Exception("NONE JSON FORMAT")
    if result:
        from crawl_engine.models import Article
        article = Article.objects.get(id=article_id)
        # article.translated_title = data['translations'][0]['translatedText']
        # article.translated_body = data['translations'][1]['translatedText']

        article.translated_title = result.get('translations')[0]
        article.translated_body = result.get('translations')[1]
        article.save()