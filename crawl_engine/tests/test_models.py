import pytest
from django.test import TestCase
from crawl_engine.models import TrashFilter, Article, SearchQuery

filter_test_data = [
    # filter domain to trash
    (TrashFilter(url='example.com'), Article(article_url='http://www.example.com/sample.html'), True),
    # do not filter domain to trash
    (TrashFilter(url='example2.com'), Article(article_url='http://www.example.com/sample.html'), False),
    # do not filter if length greater than filter
    (TrashFilter(length=100, text='JavaScipt'),
     Article(article_url='http://example.com/', body='JavaScipt' + 'a' * 100), False),
    # filter text
    (TrashFilter(length=100, text='JavaScipt'),
     Article(article_url='http://example.com/', body='JavaScipt blocked'), True),
    # filter text
    (TrashFilter(text='JavaScipt'),
     Article(article_url='http://example.com/', body='JavaScipt' + 'a' * 100), True),
    # filter from domain
    (TrashFilter(url='example.com', text='JavaScipt'),
     Article(article_url='http://example.com/', body='JavaScipt blocked'), True),
    # do not filter from other domain
    (TrashFilter(url='example.com', text='JavaScipt'),
     Article(article_url='http://example2.com/', body='JavaScipt blocked'), False)
]


@pytest.mark.parametrize("filter,article,is_trash", filter_test_data)
def test_is_trash(filter, article, is_trash):
    assert filter.is_trash(article) == is_trash


class ArticleTestCase(TestCase):

    def test_get_initial_status_keep(self):
        article = Article(channel='research')
        self.assertEqual(article.get_initial_status(), 'keep')

    def test_get_initial_status_raw(self):
        article = Article(channel='search_engines')
        self.assertEqual(article.get_initial_status(), 'raw')

    def test_get_initial_status_trash(self):
        TrashFilter.objects.create(url='example.com')
        article = Article(article_url='http://www.example.com/sample.html')
        self.assertEqual(article.get_initial_status(), 'trash')

    def test_channel_set_on_save(self):
        search = SearchQuery.objects.create(channel='research')
        article = Article(search=search)
        article.save()
        self.assertEqual(article.channel, 'research')

    def test_initial_status_set_on_save(self):
        article = Article(channel='research')
        article.save()
        self.assertEqual(article.status, 'keep')

    def test_reset_initial_status(self):
        article = Article(channel='research', status='raw')
        article.save()
        article.reset_initial_status()
        article.refresh_from_db()
        self.assertEqual(article.status, 'keep')
