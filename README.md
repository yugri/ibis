# Distributed crawler manager with API

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








  [git-repo-url]: <git@bitbucket.org:juswork/ibis_crawl_engine_jus.git>