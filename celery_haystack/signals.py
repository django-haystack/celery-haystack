from django.db.models import signals

from haystack.signals import BaseSignalProcessor
from haystack.utils import get_identifier
from haystack.exceptions import NotHandled

from .utils import get_update_task
from .indexes import CelerySearchIndex


class CelerySignalProcessor(BaseSignalProcessor):

    def setup(self):
        signals.post_save.connect(self.enqueue_save)
        signals.post_delete.connect(self.enqueue_delete)

    def teardown(self):
        signals.post_save.disconnect(self.enqueue_save)
        signals.post_delete.disconnect(self.enqueue_delete)

    def enqueue_save(self, sender, instance, **kwargs):
        return self.enqueue('update', instance, sender, **kwargs)

    def enqueue_delete(self, sender, instance, **kwargs):
        return self.enqueue('delete', instance, sender, **kwargs)

    def enqueue(self, action, instance, sender, **kwargs):
        if not hasattr(self, 'task_tls'):
            self.task_cls = get_update_task()

        """
        Given an individual model instance, determine if a backend
        handles the model, check if the index is Celery-enabled and
        enqueue task.
        """
        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            try:
                connection = self.connections[using]
                index = connection.get_unified_index().get_index(sender)
            except NotHandled:
                continue  # Check next backend

            if isinstance(index, CelerySearchIndex):
                if action == 'update' and not index.should_update(instance):
                    continue
                self.task_cls.delay(action, get_identifier(instance))
                return  # Only enqueue instance once
