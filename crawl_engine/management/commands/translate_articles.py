from datetime import datetime, timedelta

import redis
from django.core.management.base import BaseCommand
from crawl_engine.models import Article, SearchQuery
from crawl_engine.tasks import google_translate, bound_and_save, detect_lang_by_google
from crawl_engine.utils.translation_utils import separate
from celery import chord


class LimitsException(Exception):
    pass


class Command(BaseCommand):
    help = 'Translate all not translated articles'

    # def add_arguments(self, parser):
    #     parser.add_argument(name='search', nargs='*', type=str)
    #     parser.add_argument(name='article_id', nargs='*', type=str)

    def handle(self, *args, **options):
        # search = options['search']
        # article_id = options['article_id']
        # if search:
        #     articles = Article.objects.filter(
        #         search__search_id__in=options['search'],
        #         translated=False)
        # elif article_id:
        #     articles = Article.objects.filter(pk=article_id, translated=False)
        # else:
        articles = Article.objects.filter(translated=False)

        for article in articles:
            article.run_translation_task(article)

        # for article in articles:
        #     article_id = article.id
        #     # volume = len(article.body)
        #     # limiter = TranslateAPILimiter()
        #
        #     # try:
        #     #     limiter.check_access()
        #     # except LimitsException as e:
        #     #     raise
        #
        #     splitted_body = separate(article.body)
        #     splitted_title = separate(article.title)
        #     try:
        #         source = article.source_language
        #         if not source:
        #             raise ValueError("Empty source_language field.")
        #     except ValueError:
        #         print("The internal system can't detect article's language. "
        #               "Trying to detect with Google Translate API.")
        #         source = detect_lang_by_google.apply_async((splitted_body[0],))
        #     print("Detected language is: %s" % source)
        #     result_body = chord(google_translate.s(part, source) for part in splitted_body)\
        #         (bound_and_save.s(article_id, source, 'body'))
        #     print("Translation task for BODY has been queued, ID: %s" % result_body.id)
        #     result_title = chord(google_translate.s(part, source) for part in splitted_title)\
        #         (bound_and_save.s(article_id, source, 'title'))
        #     print("Translation task for TITLE has been queued, ID: %s" % result_title.id)


class TranslateAPILimiter:
    time_format = "%d/%m/%y %H:%M:%S.%f"
    connection = None

    def __init__(self):
        self.connection = redis.StrictRedis(host='localhost', port=6379, db=0)

    def check_access(self):
        timestamp_now = datetime.now()
        last_call = str(self.connection.get('last_call'), 'utf-8')
        volume = self.connection.get('volume')
        conv_time = datetime.strptime(last_call, self.time_format)
        print("Now is: %s" % timestamp_now)
        print("The last call were: %s" % conv_time)
        delta = timestamp_now - conv_time
        print("Delta: %s" % delta)
        if delta < timedelta(minutes=2):
            if int(volume) <= 2000:
                return True
            else:
                raise LimitsException("You reached to the Google's Translate API VOLUME limits")
        else:
            raise LimitsException("You reached to the Google's Translate API TIME limits")

    def update_volume(self, volume):
        now = datetime.now()
        self.connection.set('last_call', now.strftime("%d/%m/%y %H:%M:%S.%f"))
        volume = self.connection.set('volume', volume)