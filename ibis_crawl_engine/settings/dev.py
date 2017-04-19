from .common import *  # noqa


# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', True)


# Mail settings
# ------------------------------------------------------------------------------
EMAIL_PORT = 1025
EMAIL_HOST = 'localhost'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# CELERY
# ------------------------------------------------------------------------------
# In development, all tasks will be executed locally by blocking until the task returns
CELERY_ALWAYS_EAGER = True