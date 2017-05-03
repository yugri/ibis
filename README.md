+# Distributed crawler manager with API

```sh
$ git clone [git-repo-url]
```

### Local setup

```sh
$ pip install -r requirements.txt
$ ./manage.py migrate
$ ./manage.py createsuperuser
```

It's recommended to use separated virtualenv for local setup

1. You can setup your own DB or use dockerized PostgreSQL (-p 5434, -U ibis, -d articles, -p 13635724)
from <docker-compose.yml> - All credentials there.

2. Install RabbitMQ

3. Don't forget to create your own settings file. at </ibis_crawl_engine/conf>



Then start celery worker from /<project_root>:

- Start django server
```sh
python manage.py runserver
```

- Start celery worker
```sh
celery -A ibis_crawl_engine worker -l info
```

- Start celery beat
```sh
celery -A ibis_crawl_engine beat -l info
```

### Requirements:

in file <requirements.txt> & <requirements_prod.txt>

## Deploying on staging

Connect via ssh and pull new version:

```sh
$ ssh root@STAGING_IP
root@crawl:~# cd /webapps/crawler/ibis_crawl_engine
root@crawl:/webapps/crawler/ibis_crawl_engine# git pull
```

Apply migrations:

```sh
root@crawl:/webapps/crawleribis_crawl_engine# . ../venv3/bin/activate
(venv3)root@crawl:/webapps/crawler/ibis_crawl_engine# python manage.py migrate
```

Restart processes:
```sh
# django site
supervisorctl restart crawler-django
# crawler process 
supervisorctl restart celery-workers:crawler-worker
```

## Local development with Docker

1. Copy `sample.env` to  `.env` file and fill api credentials.

2. Open a terminal at the project root and run local development:

```sh
$ docker-compose -f dev.yml up
```

### Running management commands

To migrate your app and to create a superuser, run:

```sh
$ docker-compose -f dev.yml run django python manage.py migrate
$ docker-compose -f dev.yml run django python manage.py createsuperuser
```

### Run tests

To run tests run:

```sh
$ docker-compose -f dev.yml run django pytest
```

### Tests coverage

To run a simple test coverage:

```sh
$ docker-compose -f dev.yml run django pytest --cov=crawl_engine/
```

To make a pretty HTML report:

```sh
$  docker-compose -f dev.yml run django pytest --cov-report html --cov=crawl_engine/
```

Report will be saved in *htmlcov* folder.

### Code lint

We need to choose the codeguide. But for now, check newly created files against flake8

```sh
$ docker-compose -f dev.yml run django flake8
```

The config for flake8 is located in .flake8.

[git-repo-url]: <git@bitbucket.org:juswork/ibis_crawl_engine_jus.git>