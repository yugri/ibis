import feedparser
import logging

logger = logging.getLogger(__name__)


class RSSFeedParser:
    """
    Class for RSS feed parsing
    :returns seed_links: list or info message
    """
    def __init__(self, rss_link):
        self.rss_link = rss_link
        self.seed_links = []

    def parse_rss(self):
        feed = feedparser.parse(self.rss_link)
        check_entries = False
        try:
            if feed.entries is not None:
                check_entries = True
        except AttributeError as e:
            logger.info(e)
            return "Can't find entries in RSS feed, reason: %s" % e

        if check_entries:
            for entry in feed.entries:
                self.seed_links.append(entry.link)

            return self.seed_links