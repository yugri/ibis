import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip("/"))

MEDIA_URL = '/static/media/'
MEDIA_ROOT = STATIC_ROOT + MEDIA_URL

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crawlerdb',
        'USER': 'crawler',
        'PASSWORD': 'crawler',
        'HOST': 'localhost',
        'PORT': ''
    },
    # 'articles': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'articles',
    #     'USER': 'ibis',
    #     'PASSWORD': '13635724',
    #     'HOST': 'localhost',
    #     'PORT': '5434'
    # }
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

PIPELINE = {
    'PIPELINE_ENABLED': False,
}

IBIS_ADDRESS = 'http://127.0.0.1:8300/'