from django.conf import settings

from haystack.signals import RealtimeSignalProcessor
from haystack.utils import get_identifier
from haystack.exceptions import NotHandled

from celery_haystack.utils import get_update_task
from celery_haystack.indexes import CelerySearchIndex


class CelerySignalProcessor(RealtimeSignalProcessor):
    def __init__(self, *args, **kwargs):
        super(CelerySignalProcessor, self).__init__(*args, **kwargs)
        self.task_cls = get_update_task()

    def handle_save(self, sender, instance, **kwargs):
        return self.handle(sender, instance, action='update', **kwargs)

    def handle_delete(self, sender, instance, **kwargs):
        return self.handle(sender, instance, action='delete', **kwargs)

    def handle(self, sender, instance, action='update', **kwargs):
        """
        Given an individual model instance, determine if a backend
        handles the model, check if the index is Celery-enabled and
        enqueue task.
        """

        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            try:
                index = (self.connections[using].get_unified_index()
                         .get_index(sender))
            except NotHandled:
                continue  # Check next backend

            if isinstance(index, CelerySearchIndex):
                if action == 'update' and not index.should_update(instance):
                    continue
                self.enqueue(action, instance)
                return  # Only enqueue instance once

    def enqueue(self, action, instance):
        """
        Shoves a message about how to update the index into the queue.

        This is a standardized string, resembling something like::

            ``notes.note.23``
            # ...or...
            ``weblog.entry.8``
        """
        return self.task_cls.delay(action, get_identifier(instance))
