from django.core.management.base import BaseCommand
from crawl_engine.models import Article, SearchQuery
from crawl_engine.tasks import google_translate, bound_and_save, detect_lang_by_google
from crawl_engine.utils.sentence_tokenize import separate
from celery import group, chain, chord


class Command(BaseCommand):
    help = 'Translate all not translated articles'

    def add_arguments(self, parser):
        parser.add_argument('search', nargs='*')

    def handle(self, *args, **options):
        print(options['search'])
        articles = Article.objects.filter(
            search__in=SearchQuery.objects.filter(search_id=options['search']),
            translated=False).distinct()
        print(articles)

        for article in articles:
            article_id = article.id
            splitted_body = separate(article.body)
            try:
                source = article.source_language
                if not source:
                    raise ValueError("Empty source_language field.")
            except ValueError:
                print("The internal system can't detect article's language."
                "Trying to detect with Google Translate API.")
                source = detect_lang_by_google.delay(splitted_body[0]).get()
            print("Detected language is: %s" % source)
            result = chord(google_translate.s(part, source) for part in splitted_body)\
                (bound_and_save.s(article_id, source))
            print("Translation task has been queued, ID: %s" % result.id)