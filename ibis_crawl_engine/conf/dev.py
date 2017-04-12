import os
from newspaper import settings as news

from ibis_crawl_engine.conf import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DEBUG = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip("/"))
STATICFILES_LOCATION = 'static'

MEDIA_URL = STATIC_URL.strip("/") + '/media/'
MEDIA_ROOT = STATIC_ROOT + MEDIA_URL
# URL that handles the media served from MEDIA_ROOT, used for managing
# stored files.
MEDIAFILES_LOCATION = 'media'

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=['*'])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crawlerdb',
        'USER': 'crawler',
        'PASSWORD': '840402136314',
        'HOST': 'localhost',
        'PORT': ''
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'yugritsai@gmail.com'
EMAIL_HOST_PASSWORD = 'uuvzryrcqosnhefv'


ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True

PIPELINE_YUGLIFY_BINARY = '/usr/local/bin/yuglify'
PIPELINE_ENABLED = True

news.TOP_DIRECTORY = BASE_DIR

IBIS_ADDRESS = env('IBIS_ADDRESS', default=None)

# Error reports sending
ADMINS = [('Justin', 'juswork@gmail.com'), ('Vladimir', 'vladimir.ganiushev@gmail.com'),
          ('Yuri', 'yugritsai@gmail.com')]