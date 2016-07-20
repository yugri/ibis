import re
from newspaper import Article as np
from crawl_engine.utils.articleAuthorExtractor import extractArticleAuthor
from crawl_engine.utils.articleDateExtractor import extractArticlePublishedDate
from crawl_engine.utils.articleTextExtractor import extractArticleText, extractArticleTitle


class ArticleParser:
    # url = None
    # issue_id = None
    def __init__(self, url, issue_id):
        self.url = url
        self.issue_id = issue_id

    def run(self):
        # Instantiate newspaper's Article api
        page = np(self.url)
        page.download()
        page.parse()

        author = extractArticleAuthor(page.html)
        title = extractArticleTitle(page.html)
        text = page.text if page.text else extractArticleText(page.html)
        date = extractArticlePublishedDate(self.url, page.html)

        # Set our article DB model instance
        from crawl_engine.models import Article
        article = Article()

        article.article_url = page.url
        article.title = title
        article.top_image_url = page.top_image
        try:
            article.authors = author if author else article.authors[0]
        except IndexError:
            article.authors = ''

        article.body = re.sub('\n+', '\n', re.sub(' +', ' ', text))
        article.post_date_created = date

        article.save()

        return article.id




