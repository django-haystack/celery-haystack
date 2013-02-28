from django.conf import settings
from django.db.models import get_model, signals

from haystack.signals import BaseSignalProcessor
from haystack.utils import get_identifier

from celery_haystack.utils import get_update_task


class CelerySignalProcessor(BaseSignalProcessor):
    def __init__(self, *args, **kwargs):
        super(CelerySignalProcessor, self).__init__(*args, **kwargs)
        self.task_cls = get_update_task()

    def get_models(self):
        for app_model in settings.CELERY_HAYSTACK_MODELS:
            yield get_model(*app_model.rsplit('.', 1))

    def setup(self):
        for model in self.get_models():
            signals.post_save.connect(self.handle_save, sender=model)
            signals.post_delete.connect(self.handle_delete, sender=model)

    def teardown(self):
        for model in self.get_models():
            signals.post_save.disconnect(self.handle_save, sender=model)
            signals.post_delete.disconnect(self.handle_delete, sender=model)

    def handle_save(self, sender, instance, **kwargs):
        """
        Enqueue instance for update
        """
        self.enqueue_save(instance, **kwargs)

    def handle_delete(self, sender, instance, **kwargs):
        """
        Enqueue instance for deleting
        """
        self.enqueue_delete(instance, **kwargs)

    def enqueue_save(self, instance, **kwargs):
        return self.enqueue('update', instance)

    def enqueue_delete(self, instance, **kwargs):
        return self.enqueue('delete', instance)

    def enqueue(self, action, instance):
        """
        Shoves a message about how to update the index into the queue.

        This is a standardized string, resembling something like::

            ``notes.note.23``
            # ...or...
            ``weblog.entry.8``
        """
        return self.task_cls.delay(action, get_identifier(instance))
