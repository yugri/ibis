from celery import shared_task
from crawl_engine.spiders.single_url_parser import ArticleParser
from crawl_engine.utils.s3_media_loader import ImageLoader


@shared_task
def crawl_url(url, issue_id):

    parser = ArticleParser(url, issue_id)
    result = parser.run()

    return result

@shared_task
def load_image(url, article_id):
    from crawl_engine.models import Article
    loader = ImageLoader(url)
    image = loader.load()
    if image is not None:
        article = Article.objects.get(id=article_id)
        article.top_image = image
        article.save()