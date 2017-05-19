import feedparser
import logging
import requests
from datetime import datetime
from time import mktime

from crawl_engine.spiders.search_parser import SearchParser


logger = logging.getLogger(__name__)


class RSSFeedParser(SearchParser):
    """
    Class for RSS feed parsing
    """
    def __init__(self, rss_link):
        super(RSSFeedParser, self).__init__()
        self.rss_link = rss_link

    def run(self):
        r = requests.get(self.rss_link)
        feed = feedparser.parse(r.text)

        result = []
        for entry in feed.entries:
            article = self._new_article(entry.link, entry.title, entry.description)
            article['post_date_created'] = datetime.fromtimestamp(mktime(entry.published_parsed))
            result.append(article)

        return result
