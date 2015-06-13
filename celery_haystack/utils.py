from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.db import connection

from haystack.utils import get_identifier

from .conf import settings


def get_update_task(task_path=None):
    import_path = task_path or settings.CELERY_HAYSTACK_DEFAULT_TASK
    module, attr = import_path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))
    try:
        Task = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, attr))
    return Task()


def enqueue_task(action, instance):
    """
    Common utility for enqueing a task for the given action and
    model instance.
    """
    identifier = get_identifier(instance)
    kwargs = {}
    if settings.CELERY_HAYSTACK_QUEUE:
        kwargs['queue'] = settings.CELERY_HAYSTACK_QUEUE
    if settings.CELERY_HAYSTACK_COUNTDOWN:
        kwargs['countdown'] = settings.CELERY_HAYSTACK_COUNTDOWN
    task = get_update_task()
    if hasattr(connection, 'on_commit'):
        connection.on_commit(
            lambda: task.apply_async((action, identifier), {}, **kwargs)
        )
    else:
        task.apply_async((action, identifier), {}, **kwargs)
