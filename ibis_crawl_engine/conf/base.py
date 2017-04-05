# TODO: import is a bad pracice, remove it
from . import *  # noqa
from .assets import *  # noqa

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///ibis_crawl_engine'),
}
