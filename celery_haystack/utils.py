from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def get_update_task():
    task_path = getattr(settings, 'CELERY_HAYSTACK_DEFAULT_TASK',
                                  'celery_haystack.tasks.CeleryHaystackSignalHandler')
    module, attr = task_path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))
    try:
        Task = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, attr))
    return Task()
