===============
celery-haystack
===============

Allows you to utilize a queue and shove updates/deletes for search into it,
keeping your pages fast and your index fresh.

For use with Haystack (http://haystacksearch.org/).

Requirements
============

* Django 1.2+
* Haystack 2.0.X (http://github.com/toastdriven/django-haystack)
* Celery 1.X (http://celeryproject.org/)

You also need to install your choice of one of the supported search engines
for Haystack and one of the supported backends for Celery.


Setup
=====

#. Add ``celery_haystack`` to ``INSTALLED_APPS``.
#. Alter all of your ``SearchIndex`` subclasses to inherit from
   ``celery_haystack.indexes.CelerySearchIndex`` (as well as
   ``indexes.Indexable``).
#. Ensure your Celery instance is running.
#. PROFIT!
