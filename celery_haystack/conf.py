from django.conf import settings
from haystack import constants
from appconf import AppConf


class CeleryHaystack(AppConf):
    DEFAULT_ALIAS = None
    RETRY_DELAY = 5 * 60
    MAX_RETRIES = 1
    DEFAULT_TASK = 'celery_haystack.tasks.CeleryHaystackSignalHandler'

    COMMAND_BATCH_SIZE = None
    COMMAND_AGE = None
    COMMAND_REMOVE = False
    COMMAND_WORKERS = 0
    COMMAND_APPS = []
    COMMAND_VERBOSITY = 1

    def configure_default_alias(self, value):
        return value or getattr(constants, 'DEFAULT_ALIAS', None)

    def configure(self):
        data = {}
        for name, value in self.configured_data.items():
            if name in ('RETRY_DELAY', 'MAX_RETRIES',
                        'COMMAND_WORKERS', 'COMMAND_VERBOSITY'):
                value = int(value)
            data[name] = value
        return data
