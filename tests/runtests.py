#!/usr/bin/env python
import sys
from os import path

from django.conf import settings

TEST_ROOT = path.abspath(path.dirname(__file__))

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'haystack',
            'djcelery',
            'celery_haystack',
            'notes',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        HAYSTACK_CONNECTIONS={
            'default': {
                'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
                'PATH': path.join(TEST_ROOT, 'whoosh_index'),
            }
        },
        BROKER_TRANSPORT="memory",
        CELERY_IGNORE_RESULT=True,
        CELERYD_LOG_LEVEL="DEBUG",
        CELERY_DEFAULT_QUEUE="celery-haystack",
    )

from django.test.simple import run_tests


def runtests(*test_args):
    if not test_args:
        test_args = ['notes']
    sys.path.insert(0, TEST_ROOT)
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
