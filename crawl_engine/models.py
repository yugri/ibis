import io
from time import sleep

import requests
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models


class Article(models.Model):
    article_url = models.URLField()
    source_language = models.CharField(max_length=5, blank=True, null=True)
    title = models.CharField(max_length=240, blank=True)
    translated_title = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True)
    translated_body = models.TextField(blank=True)
    authors = models.CharField(max_length=240, blank=True)
    post_date_created = models.CharField(max_length=50, blank=True)
    post_date_crawled = models.DateField(auto_now_add=True, null=True)
    translated = models.BooleanField(default=False)
    top_image_url = models.URLField(blank=True)
    top_image = models.ImageField(upload_to='article-images', blank=True, null=True)
    search_id = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        img_url = self.top_image_url
        if img_url and not self.top_image:
            filename = str(hash(img_url))
            self.set_image(img_url, filename)

        super(Article, self).save(*args, **kwargs)

    def set_image(self, url, filename):
        try:
            sleep(1)
            r = requests.get(url, stream=True)
        except requests.ConnectionError as e:
            r = None
            self.logger.error(e)

        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            img_io = io.BytesIO()
            img.save(img_io, format=img.format)
            image_name = "{0}.{1}".format(filename, str(img.format).lower())
            self.top_image.save(image_name, ContentFile(img_io.getvalue()))


class Task(models.Model):
    task_id = models.CharField(max_length=50)
    tstamp = models.DateTimeField(auto_now=True)