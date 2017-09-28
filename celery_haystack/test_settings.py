import os

from celery import Celery

app = Celery('celery_haystack')
app.config_from_object('django.conf:settings')


DEBUG = True

TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests'))

INSTALLED_APPS = [
    'haystack',
    'celery_haystack',
    'celery_haystack.tests',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'really-not-secret'

BROKER_TRANSPORT = "memory"
CELERY_ALWAYS_EAGER = True
CELERY_IGNORE_RESULT = True
CELERYD_LOG_LEVEL = "DEBUG"
CELERY_DEFAULT_QUEUE = "celery-haystack"

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(TEST_ROOT, 'whoosh_index'),
    }
}
HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
