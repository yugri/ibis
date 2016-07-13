from django.db import models

# Create your models here.


class Article(models.Model):
    article_url = models.URLField()
    title = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True)
    authors = models.CharField(max_length=240, blank=True)
    post_date_created = models.DateTimeField(blank=True)
    post_date_crawled = models.DateField(auto_now_add=True, null=True)


class ArticleImages(models.Model):
    image = models.ImageField(upload_to='/article-images')
    article = models.ForeignKey(Article)


class Task(models.Model):
    task_id = models.CharField(max_length=50)
    tstamp = models.DateTimeField(auto_now=True)