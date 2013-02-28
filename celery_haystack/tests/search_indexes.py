from haystack import indexes, __version__ as haystack_version
from .models import Note

if haystack_version[:2] < (2, 0):
    from celery_haystack.indexes import CelerySearchIndex as SearchIndex
    from haystack import site

    class Indexable(object):
        pass
    indexes.Indexable = Indexable
else:
    SearchIndex = indexes.SearchIndex  # noqa
    site = None  # noqa


# Simplest possible subclass that could work.
class NoteIndex(SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='content')

    def get_model(self):
        return Note

if site:
    site.register(Note, NoteIndex)
