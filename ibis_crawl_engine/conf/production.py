import os

from django.utils import six

from ibis_crawl_engine.conf import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip("/"))

MEDIA_URL = '/media/'
MEDIA_ROOT = STATIC_ROOT + MEDIA_URL

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

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

# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/index.html
INSTALLED_APPS += (
    'storages',
)

AWS_ACCESS_KEY_ID = 'AKIAIWBLWFT2XKFAAMUA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'crawler-storage'
AWS_AUTO_CREATE_BUCKET = False
AWS_PRELOAD_METADATA = True
AWS_S3_SECURE_URLS = True
AWS_QUERYSTRING_AUTH = False
# AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()

# AWS cache settings, don't change unless you know what you're doing:
AWS_EXPIRY = 60 * 60 * 24 * 7

# Revert the following and use str after the above-mentioned bug is fixed in
# either django-storage-redux or boto
AWS_HEADERS = {
    'Cache-Control': six.b('max-age=%d, s-maxage=%d, must-revalidate' % (
        AWS_EXPIRY, AWS_EXPIRY))
}

# URL that handles the media served from MEDIA_ROOT, used for managing
# stored files.
MEDIAFILES_LOCATION = 'media'
MEDIA_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_STORAGE_BUCKET_NAME, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'config.s3_config.MediaStorage'



# Static Assets
# ------------------------
STATICFILES_STORAGE = 'config.s3_config.StaticStorage'
STATICFILES_LOCATION = 'static'
COMPRESS_URL = "https://%s.s3.amazonaws.com/%s/" % (AWS_STORAGE_BUCKET_NAME, STATICFILES_LOCATION)

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