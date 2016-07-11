from scrapy import Item, Field


class NewsItem(Item):
    title = Field()
    body = Field()