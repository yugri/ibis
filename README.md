# Distributed crawler manager with API

### Requirements:

*[MongoDB] - Modern NoSQL database

### Local setup

It's recommended to use separated virtualenv for local setup

```sh
$ git clone [repo-url]
```

```sh
$ pip install requirements.txt
$ ./manage.py makemigrations
$ ./manage.py migrate
$ ./manage.py createsuperuser
```

Then start celery worker from /<project_root>:
```sh
celery -A ibis_crawl_engine worker -l info
```

  [MongoDB]: <https://www.mongodb.com/>
  [repo-url]: <https://yugritsai@bitbucket.org/teamoffortune/ibis_crawl_engine.git>