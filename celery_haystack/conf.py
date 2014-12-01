from django.conf import settings  # noqa
from django.core.exceptions import ImproperlyConfigured
from haystack import constants, __version__ as haystack_version
from haystack.management.commands import update_index as cmd
from appconf import AppConf


class CeleryHaystack(AppConf):
    #: The default alias to
    DEFAULT_ALIAS = None
    #: The delay (in seconds) before task will be executed (Celery countdown)
    COUNTDOWN = 0
    #: The delay (in seconds) after which a failed index is retried
    RETRY_DELAY = 5 * 60
    #: The number of retries that are done
    MAX_RETRIES = 1
    #: The default Celery task class
    DEFAULT_TASK = 'celery_haystack.tasks.CeleryHaystackSignalHandler'
    #: The name of the celery queue to use, or None for default
    QUEUE = None
    #: Whether the task should be handled transaction safe
    TRANSACTION_SAFE = True

    #: The batch size used by the CeleryHaystackUpdateIndex task
    COMMAND_BATCH_SIZE = None
    #: The max age of items used by the CeleryHaystackUpdateIndex task
    COMMAND_AGE = None
    #: Wehther to remove items from the index that aren't in the DB anymore
    COMMAND_REMOVE = False
    #: The number of multiprocessing workers used by the CeleryHaystackUpdateIndex task
    COMMAND_WORKERS = 0
    #: The names of apps to run update_index for
    COMMAND_APPS = []
    #: The verbosity level of the update_index call
    COMMAND_VERBOSITY = 1

    def configure_default_alias(self, value):
        return value or getattr(constants, 'DEFAULT_ALIAS', None)

    def configure_command_batch_size(self, value):
        return value or getattr(cmd, 'DEFAULT_BATCH_SIZE', None)

    def configure_command_age(self, value):
        return value or getattr(cmd, 'DEFAULT_AGE', None)

    def configure(self):
        data = {}
        for name, value in self.configured_data.items():
            if name in ('RETRY_DELAY', 'MAX_RETRIES',
                        'COMMAND_WORKERS', 'COMMAND_VERBOSITY'):
                value = int(value)
            data[name] = value
        return data


signal_processor = getattr(settings, 'HAYSTACK_SIGNAL_PROCESSOR', None)


if haystack_version[0] >= 2 and signal_processor is None:
    raise ImproperlyConfigured("When using celery-haystack with Haystack 2.X "
                               "the HAYSTACK_SIGNAL_PROCESSOR setting must be "
                               "set. Use 'celery_haystack.signals."
                               "CelerySignalProcessor' as default.")
