import datetime
from django.db import models


# Ghetto app!
class Note(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()
    author = models.CharField(max_length=64)
    created = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.title
