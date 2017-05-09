import pytest

from crawl_engine.models import TrashFilter, Article

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