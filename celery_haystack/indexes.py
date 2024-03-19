from haystack import indexes


class CelerySearchIndex(indexes.SearchIndex):
    
    def update_object(self, instance, using=None, **kwargs):
        """Remove an object if it is no longer in the index_queryset"""

        ids = self.index_queryset(**kwargs).values_list('id', flat=True)
        if instance.id not in ids:
            self.remove_object(instance)
        else:
            super(ProjectIndex, self).update_object(instance, using, **kwargs)
