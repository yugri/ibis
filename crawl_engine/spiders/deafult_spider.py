import logging
from scrapy import Spider
from scrapy.spiders import CrawlSpider

from crawl_engine.items import NewsItem


class DefaultNewsSpider(Spider):
    name = 'default_spider'
    query_url = ''
    issue_id = ''
    allowed_domains = ["news.google.com.ua"]
    start_urls = ["https://news.google.com.ua/"]

    def __init__(self, *args, **kwargs):
        super(DefaultNewsSpider, self).__init__(*args, **kwargs)
        query_url = kwargs.get('query_url', None)
        issue_id = kwargs.get('issue_id', None)
        if query_url is not None:
            self.query_url = query_url
        else:
            raise BaseException("Define a --query_url parameter please")

    def parse(self, response):
        self.logger.info("Crawler initialisation...")

        item = NewsItem()
        item['title'] = "This is a test item's title."
        item['body'] = "Thi is a test item's body. Should be an article body here."
        item['issue_id'] = self.issue_id
        yield item

