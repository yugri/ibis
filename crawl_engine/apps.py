from django.apps import AppConfig


class CrawlEngineConfig(AppConfig):
    name = 'crawl_engine'

    def ready(self):
        import crawl_engine.signals
