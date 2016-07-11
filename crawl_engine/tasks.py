from __future__ import absolute_import
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawl_engine.spiders.deafult_spider import DefaultNewsSpider
from celery import shared_task
from celery.utils.log import get_task_logger


@shared_task
def run_default_spider(query):
    # logger = get_task_logger(__name__)
    process = CrawlerProcess(get_project_settings())
    # logger.info("Crawler process initialised...")
    process.crawl(DefaultNewsSpider, query_url=None, issue_id=None)
    # logger.info("__***__ Crawler starting... __***__")
    process.start() # the script will block here until the crawling is finished


@shared_task
def mul(x, y):
    return x * y
