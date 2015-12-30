from haystack import indexes

from .models import Note
from ..indexes import CelerySearchIndex


# Simplest possible subclass that could work.
class NoteIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='content')

    def get_model(self):
        return Note
