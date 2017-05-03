import io
import requests
import logging
from time import sleep
from datetime import datetime, timedelta
from PIL import Image
from celery import chord
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.timezone import utc
from django.contrib.postgres.fields import JSONField

from crawl_engine.common.constants import TYPES, CHANNELS, PERIODS, STATUSES
from crawl_engine.utils.article_processing_utils import is_url_image
from crawl_engine.utils.text_processing_utils import separate


logger = logging.getLogger(__name__)


class LanguageDetectionError(BaseException):
    pass


class SearchQuery(models.Model):
    search_id = models.CharField(max_length=50, db_index=True)
    search_type = models.CharField(max_length=20, choices=TYPES, default='search_engine')
    article_url = models.CharField(max_length=1000, blank=True, null=True)
    rss_link = models.CharField(max_length=1000, blank=True, null=True)
    query = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=200, default='google',
                              help_text='Type please with 1 backspace and 1 coma btw words. Ex.: google, yahoo')
    channel = models.CharField(max_length=64, choices=CHANNELS, default='general', db_column='search_channel')
    search_depth = models.PositiveIntegerField(default=10)
    active = models.BooleanField(default=True)
    period = models.CharField(max_length=20, choices=PERIODS, default='daily')
    last_processed = models.DateTimeField(blank=True, null=True)
    response_address = models.CharField(max_length=50, blank=True, null=True, default=None)
    options = JSONField(blank=True, null=True)
    email_links = JSONField(blank=True, null=True)

    @property
    def get_sources(self):
        return self.source.split(', ')

    @property
    def time_period(self):
        if self.period == "hourly":
            return timedelta(hours=1)
        elif self.period == "daily":
            return timedelta(days=1)
        elif self.period == "weekly":
            return timedelta(weeks=1)
        else:
            return timedelta(days=30)

    @property
    def expired_period(self):
        now = datetime.utcnow().replace(tzinfo=utc)

        if not self.last_processed or now - self.last_processed > self.time_period:
            return True

    @property
    def remote_addr(self):
        return 'http://{0}/'.format(self.response_address)

    def __str__(self):
        return "{0} [{1}]".format(self.search_id, self.search_type)

    def clean(self):
        source_choices = [x[0] for x in settings.SOURCES]
        for source in self.get_sources:
            if source not in source_choices:
                raise ValidationError("Can't resolve a source type: %s.\n"
                                      "Choices are: %s" % (source, str(source_choices)))


class SearchTask(models.Model):
    task_id = models.CharField(primary_key=True, max_length=50, blank=False)
    search_query = models.ForeignKey(SearchQuery, blank=True)


class Article(models.Model):
    article_url = models.URLField(max_length=2048, db_index=True)
    source_language = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=1000, blank=True, db_index=True)
    translated_title = models.CharField(max_length=1000, blank=True)
    body = models.TextField(blank=True, null=True)
    translated_body = models.TextField(blank=True, null=True)
    authors = models.CharField(max_length=1000, blank=True, null=True)
    post_date_created = models.CharField(max_length=50, blank=True)
    post_date_crawled = models.DateTimeField(auto_now_add=True, null=True)
    translated = models.BooleanField(default=False, db_index=True)
    top_image_url = models.URLField(max_length=1000, blank=True)
    top_image = models.ImageField(upload_to='article-images', blank=True, null=True, max_length=1000)
    file = models.FileField(upload_to='article-files', blank=True, null=True)
    search = models.ForeignKey(SearchQuery, blank=True, null=True, related_name='articles')
    processed = models.BooleanField(default=False, db_index=True)
    pushed = models.BooleanField(default=False, db_index=True)

    status = models.CharField(choices=STATUSES, max_length=50, blank=True, null=True)
    channel = models.CharField(choices=CHANNELS, max_length=50, blank=True, null=True)

    # Stores articles locations (lat, lng, place)
    locations = JSONField(blank=True, null=True)

    # Article tags
    tags = models.ManyToManyField('tagging.Tag', blank=True)

    # Fields from OLD IBIS
    domains = JSONField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.article_url

    @property
    def short_url(self):
        return truncatechars(self.article_url, 30)

    def save(self, start_translation=False, push=False, upload_file=False, *args, **kwargs):
        img_url = self.top_image_url
        if is_url_image(img_url) and not self.top_image:
            # TODO: Rewrite this behavior to save images and files in async mode
            filename = str(hash(img_url))
            self.set_image(img_url, filename)

        if not self.status:
            self.article_status_from_search()

        super(Article, self).save(*args, **kwargs)

        if start_translation:
            self.run_translation_task(self)
        if push:
            self.push_article()
        if upload_file:
            self.run_file_upload_task()

    def set_image(self, url, filename):
        # This method executes new request to the resource
        # for loading articles top_image
        try:
            sleep(1)
            r = requests.get(url, stream=True)
        except requests.ConnectionError as e:
            r = None
            logger.error(e)
            pass

        if r is not None and r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            img_io = io.BytesIO()
            img.save(img_io, format=img.format)
            image_name = "{0}.{1}".format(filename, str(img.format).lower())
            self.top_image.save(image_name, ContentFile(img_io.getvalue()))

    def run_file_upload_task(self):
        from crawl_engine.tasks import upload_file
        # TODO: return some stuff after task running
        upload_file.apply_async((self.article_url, self.id))

    def run_translation_task(self, instance):
        from crawl_engine.tasks import google_translate, detect_lang_by_google, bound_and_save

        if not instance.translated:
            article_id = instance.id
            splitted_body = separate(instance.body)
            splitted_title = separate(instance.title)

            # Check article's source_language
            try:
                source = instance.source_language
                if not source:
                    raise ValueError("Empty source_language field.")
            # If var is empty try to detect with Google's Translate API
            except ValueError:
                logger.info("The internal system can't detect article's language. "
                            "Trying to detect with Google Translate API.")
                source = detect_lang_by_google(splitted_body[0])
            logger.info("Detected language is: %s" % source)

            # Recheck source_language again
            try:
                if source == 'und':  # Google Translate API returns 'und' if can't detect language
                    raise LanguageDetectionError("Google Translate API can't detect language")
            except LanguageDetectionError as e:
                logger.info(e)
                source = None
                instance.delete(keep_parents=True)
                logger.info("Article was deleted due to LanguageDetectionError")

            if source:
                # Check if detected language is English. If YES we store the
                # translated_title and translated_body the same title and body
                if source == "en":
                    instance.source_language = source
                    instance.translated_title = instance.title
                    instance.translated_body = instance.body
                    instance.translated = True
                    instance.save(start_translation=False)
                    logger.info("No need to execute the translation task because article's language is EN.")
                # Else run translation tasks. Tasks will run separately for the body and the title.
                else:
                    result_body = chord([google_translate.s(part, source)
                                        for part in splitted_body])(bound_and_save.s(article_id, source, 'body'))
                    logger.info("Translation task for BODY has been queued, ID: %s" % result_body.id)
                    result_title = chord([google_translate.s(part, source)
                                         for part in splitted_title])(bound_and_save.s(article_id, source, 'title'))
                    logger.info("Translation task for TITLE has been queued, ID: %s" % result_title.id)

    def run_entities_collecting_task(self):
        from crawl_engine.tasks import get_geo_entity_for_article
        get_geo_entity_for_article.apply_async((self.id,))

    @property
    def related_search_id(self):
        """
        Gets search_id from related Search
        :return: search_id [str]
        """
        return self.search.search_id

    def push_article(self):
        """
        Method for pushing an article to IBIS through it's API endpoint
        :return: nothing
        """
        raise NotImplementedError

    def article_status_from_search(self):
        search_channel = self.search.channel

        if search_channel in ['industry', 'research', 'government', 'other']:
            status = 'keep'
        else:
            status = 'raw'
        return status, search_channel


class BlockedSite(models.Model):
    """
    Sites, that need to be omitted by crawler
    """
    ibis_site_id = models.CharField(max_length=20)
    site = models.CharField(
        max_length=255,
        help_text='''
            To block entire domain use <b>example\.com</b>.
            To block subdomain use <b>sub\.example\.com</b>.
            To blcok specific files from domain use <b>sub\.example\.com.*\.pdf</b>.
            You can test expressions in <a href="http://regexr.com/" target="_blank">online tool</a>.
        ''',
        verbose_name='Block url regexp')

    def __str__(self):
        return self.site
