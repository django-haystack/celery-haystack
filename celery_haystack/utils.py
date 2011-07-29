from django.conf import settings

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from django.utils.importlib import import_module


def get_update_task(task_path=None):
    from celery_haystack import conf
    import_path = task_path or conf.DEFAULT_TASK
    module, attr = import_path.rsplit('.', 1)
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


class Setting(SimpleLazyObject):
    """
    A settings object that can check an arbitrary holder for its value.
    """
    def __init__(self, name, default=None, holder=None):
        self.__dict__.update({
            'name': name,
            'default': default,
            'holder': holder or settings,
        })
        super(Setting, self).__init__(self.setup)

    def setup(self):
        return getattr(self.holder, self.name, self.default)
