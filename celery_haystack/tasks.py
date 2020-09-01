from celery.app import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

from .utils import get_handler
from . import exceptions
from .conf import settings

logger = get_task_logger(__name__)


@shared_task(bind=True,
             using=settings.CELERY_HAYSTACK_DEFAULT_ALIAS,
             max_retries=settings.CELERY_HAYSTACK_MAX_RETRIES,
             default_retry_delay=settings.CELERY_HAYSTACK_RETRY_DELAY)
def haystack_signal_handler(self, action, identifier, **kwargs):
    try:
        get_handler()(identifier).handle(action)
    except exceptions.IndexOperationException as exc:
        logger.exception(exc)
        self.retry(exc=exc)
    except exceptions.InstanceNotFoundException as exc:
        logger.error(exc)
    except exceptions.UnrecognizedActionException as exc:
        logger.error("%s. Moving on..." % action)


@shared_task()
def celery_haystack_update_index(apps=None, **kwargs):
    """
    A celery task class to be used to call the update_index management
    command from Celery.
    """
    defaults = {
        'batchsize': settings.CELERY_HAYSTACK_COMMAND_BATCH_SIZE,
        'age': settings.CELERY_HAYSTACK_COMMAND_AGE,
        'remove': settings.CELERY_HAYSTACK_COMMAND_REMOVE,
        'using': [settings.CELERY_HAYSTACK_DEFAULT_ALIAS],
        'workers': settings.CELERY_HAYSTACK_COMMAND_WORKERS,
        'verbosity': settings.CELERY_HAYSTACK_COMMAND_VERBOSITY,
    }
    defaults.update(kwargs)
    if apps is None:
        apps = settings.CELERY_HAYSTACK_COMMAND_APPS
    # Run the update_index management command
    logger.info("Starting update index")
    call_command('update_index', *apps, **defaults)
    logger.info("Finishing update index")
