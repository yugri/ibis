import re
from newspaper import Article as np
from crawl_engine.utils.articleAuthorExtractor import extractArticleAuthor
from crawl_engine.utils.articleDateExtractor import extractArticlePublishedDate
from crawl_engine.utils.articleTextExtractor import extractArticleText, extractArticleTitle
from langdetect import detect


class ArticleParser:

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

        # Detect article source language at this point.
        # If language is 'en' we save an <article.translated_title>
        # and <article.translated_body> same as <title> and <body>.
        title_lang = detect(title)
        text_lang = detect(text)
        if title_lang == 'en' and text_lang == 'en':
            article.translated_title = title
            article.translated_body = text
            article.translated = True

        article.source_language = text_lang if text_lang == title_lang else None
        article.save()

        return article.id

    def download_image(self, article_instance):
        article_url = self.url
        page = np(self.url)
        page.download()
        page.parse()
        article_instance.top_image_url = page.top_image
        article_instance.save()





