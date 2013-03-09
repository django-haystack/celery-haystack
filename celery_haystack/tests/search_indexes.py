from haystack import indexes, __version__ as haystack_version

from .models import Note
from ..indexes import CelerySearchIndex

if haystack_version[:2] < (2, 0):
    from haystack import site

    class Indexable(object):
        pass
    indexes.Indexable = Indexable
else:
    site = None  # noqa


# Simplest possible subclass that could work.
class NoteIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='content')

    def get_model(self):
        return Note

if site:
    site.register(Note, NoteIndex)
