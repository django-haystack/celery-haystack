from django.db.models import signals

from haystack import indexes

from .utils import enqueue_task


class CelerySearchIndex(indexes.SearchIndex):
    """
    A ``SearchIndex`` subclass that enqueues updates/deletes for later
    processing using Celery.
    """
    # We override the built-in _setup_* methods to connect the enqueuing
    # operation.
    def _setup_save(self, model):
        signals.post_save.connect(self.enqueue_save,
                                  sender=model,
                                  dispatch_uid=CelerySearchIndex)

    def _setup_delete(self, model):
        signals.post_delete.connect(self.enqueue_delete,
                                    sender=model,
                                    dispatch_uid=CelerySearchIndex)

    def _teardown_save(self, model):
        signals.post_save.disconnect(self.enqueue_save,
                                     sender=model,
                                     dispatch_uid=CelerySearchIndex)

    def _teardown_delete(self, model):
        signals.post_delete.disconnect(self.enqueue_delete,
                                       sender=model,
                                       dispatch_uid=CelerySearchIndex)

    def enqueue_save(self, instance, **kwargs):
        if not getattr(instance, 'skip_indexing', False):
            return self.enqueue('update', instance)

    def enqueue_delete(self, instance, **kwargs):
        if not getattr(instance, 'skip_indexing', False):
            return self.enqueue('delete', instance)

    def enqueue(self, action, instance):
        """
        Shoves a message about how to update the index into the queue.

        This is a standardized string, resembling something like::

            ``notes.note.23``
            # ...or...
            ``weblog.entry.8``
        """
        return enqueue_task(action, instance)
