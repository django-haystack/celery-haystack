from django.core.exceptions import ImproperlyConfigured
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module
from django.db import connection, transaction

from haystack.utils import get_identifier

from .conf import settings


def get_class(import_path):
    module_name, attr = import_path.rsplit('.', 1)
    try:
        mod = import_module(module_name)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module_name, e))
    try:
        update_task = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module_name, attr))
    return update_task


def get_update_task(task_path=None):
    import_path = task_path or settings.CELERY_HAYSTACK_DEFAULT_TASK
    return get_class(import_path)


def enqueue_task(action, instance, **kwargs):
    """
    Common utility for enqueing a task for the given action and
    model instance.
    """
    identifier = get_identifier(instance)
    options = {}
    if settings.CELERY_HAYSTACK_QUEUE:
        options['queue'] = settings.CELERY_HAYSTACK_QUEUE
    if settings.CELERY_HAYSTACK_COUNTDOWN:
        options['countdown'] = settings.CELERY_HAYSTACK_COUNTDOWN

    task = get_update_task()
    task_func = lambda: task.apply_async((action, identifier), kwargs, **options)

    if hasattr(transaction, 'on_commit'):
        # Django 1.9 on_commit hook
        transaction.on_commit(
            task_func
        )
    elif hasattr(connection, 'on_commit'):
        # Django-transaction-hooks
        connection.on_commit(
            task_func
        )
    else:
        task_func()


def get_handler():
    return get_class(settings.CELERY_HAYSTACK_HANDLER)
