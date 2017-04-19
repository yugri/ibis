from __future__ import absolute_import

import os, environ

from kombu import Exchange, Queue
from newspaper import settings as news

from .assets import *




ROOT_DIR = environ.Path(__file__) - 3

env = environ.Env()
environ.Env.read_env('{}/.env'.format(ROOT_DIR))


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


###################
# Celery settings #
###################
BROKER_URL = env('BROKER_URL', default='amqp://guest:guest@localhost:5672/')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_IGNORE_RESULT = False
CELERY_CACHE_BACKEND = env('CELERY_CACHE_BACKEND', default='redis://localhost:6379/0')
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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@tx^51!8eobmvlrq$ytrfb9&bya6vvysp*lvy-%q#-rh(05+)p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=False)

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
    'crawl_engine.apps.CrawlEngineConfig',
    'dashboard.apps.DashboardConfig',
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
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip('/'))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL.strip('/'))

# URL that handles the media served from MEDIA_ROOT, used for managing
# stored files.
MEDIAFILES_LOCATION = 'media'


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

YANDEX_API_USER = env.get_value('YANDEX_API_USER', default=None)
YANDEX_API_KEY = env.get_value('YANDEX_API_KEY', default=None)

SOCIAL_SEARCHER_API_KEY = env.get_value('SOCIAL_SEARCHER_API_KEY', default='03843432f3924bc3fa501b9e03c2d792')

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

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgresql://ibis:13635724@0.0.0.0:5433/ibis'),
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'yugritsai@gmail.com'
EMAIL_HOST_PASSWORD = 'uuvzryrcqosnhefv'

IBIS_ADDRESS = env('IBIS_ADDRESS', default='http://endlessripples.com.au/')


ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True

PIPELINE_ENABLED = False
PIPELINE_YUGLIFY_BINARY = '/usr/local/bin/yuglify'

news.TOP_DIRECTORY = BASE_DIR


# Error reports sending
ADMINS = (
    ('Justin', 'juswork@gmail.com'),
    ('Vladimir', 'vladimir.ganiushev@gmail.com'),
    ('Yuri', 'yugritsai@gmail.com')
)
