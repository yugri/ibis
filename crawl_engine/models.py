from django.db import models
from crawl_engine.tasks import load_image

# Create your models here.


class Article(models.Model):
    article_url = models.URLField()
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

    def save(self, *args, **kwargs):
        img_url = self.top_image_url
        if img_url and not self.top_image:
            load_image_task = load_image(self.top_image_url, self.pk)
        super(Article, self).save(*args, **kwargs)


class Task(models.Model):
    task_id = models.CharField(max_length=50)
    tstamp = models.DateTimeField(auto_now=True)