from django.db import models

# Create your models here.


class Article(models.Model):
    article_url = models.URLField()
    title = models.CharField(max_length=240)
    body = models.TextField()
    author = models.CharField(max_length=240)
    post_date_created = models.DateField()
    post_date_crawled = models.DateField(auto_created=True)


class ArticleImages(models.Model):
    image = models.ImageField(upload_to='/article-images')
    article = models.ForeignKey(Article)


class Task(models.Model):
    task_id = models.CharField(max_length=50)
    tstamp = models.DateTimeField(auto_now=True)