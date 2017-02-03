from __future__ import absolute_import

from kombu import Exchange

"""
Django settings for ibis_crawl_engine project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import environ
from kombu import Queue
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env()  # reading .env file

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "ibis_news_db"
MONGODB_COLLECTION = "articles"

###################
# Celery settings #
###################
BROKER_URL = 'amqp://guest:guest@localhost:2672//'
# BROKER_URL = 'redis://localhost:6379/0'
# BROKER_HEARTBEAT = 0
# CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_IGNORE_RESULT = False
CELERY_CACHE_BACKEND = 'redis://localhosto:6379/0'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_MONGODB_BACKEND_SETTINGS = {
#     'database': MONGODB_DB,
#     'taskmeta_collection': 'task_meta',
# }
CELERYD_MAX_TASKS_PER_CHILD = 100

CELERY_ACCEPT_CONTENT = ['pickle', 'json']

CELERY_DEFAULT_QUEUE = 'crawler'

CELERY_QUEUES = (
    Queue('crawler', Exchange('crawler'), routing_key='crawler_task.#'),
    Queue('translation', Exchange('translation'), routing_key='translation_task.#'),
    Queue('alchemy', Exchange('alchemy'), routing_key='alchemy_task.#'),
    Queue('uploader', Exchange('uploader'), routing_key='uploader_task.#'),
)

CELERY_ROUTES = {
    'crawl_engine.tasks.detect_lang_by_google': {
        'queue': 'translation',
    },
    'crawl_engine.tasks.google_translate': {
        'queue': 'translation',
    },
    'crawl_engine.tasks.google_detect_translate': {
        'queue': 'translation',
    },
    'crawl_engine.tasks.upload_articles': {
        'queue': 'uploader',
    },
    'crawl_engine.tasks.get_geo_entity_for_article': {
        'queue': 'alchemy',
    },
}

# CELERY_DEFAULT_EXCHANGE = 'tasks'
# CELERY_DEFAULT_EXCHANGE_TYPE = 'crawler'
# CELERY_DEFAULT_ROUTING_KEY = 'task.default'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@tx^51!8eobmvlrq$ytrfb9&bya6vvysp*lvy-%q#-rh(05+)p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
    'rest_framework',
    'crawl_engine',
    'dashboard',
    'tagging.apps.TaggingConfig',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ibis_crawl_engine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['dashboard/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ibis_crawl_engine.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

GOOGLE_TRANSLATE_API_KEY = env.get_value('GOOGLE_TRANSLATE_API_KEY', default=None)
CSE_ID = env.get_value('CSE_ID', default=None)  # The custom search engine ID

SOURCES = (
    ('google', 'Google'),
    ('google_cse', 'Google CSE'),
    ('google_blogs', 'Google Blogs'),
    ('google_news', 'Google News'),
    ('google_scholar', 'Google Scholar'),
    ('bing', 'Bing'),
    ('yandex', 'Yandex')
)

ALCHEMY_API_KEY = env('ALCHEMY_API_KEY')

IBIS_ADDRESS = None


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
