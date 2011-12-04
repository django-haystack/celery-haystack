from .base import *

HAYSTACK_SITECONF = 'celery_haystack.tests.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = path.join(TEST_ROOT, 'whoosh_index')
