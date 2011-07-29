===============
celery-haystack
===============

This Django app allows you to utilize Celery for automatically updating and
deleting objects in a Haystack_ search index.

Requirements
------------

* Django 1.2+
* Haystack_ `2.0.X`_
* Celery_ 1.X

You also need to install your choice of one of the supported search engines
for Haystack and one of the supported backends for Celery.

.. _Haystack: http://haystacksearch.org
.. _`2.0.X`: https://github.com/toastdriven/django-haystack

Installation
------------

Use your favorite Python package manager to install the app from PyPI::

    pip install celery-haystack

Setup
-----

1. Add ``'celery_haystack'`` to ``INSTALLED_APPS``.
2. Alter all of your ``SearchIndex`` subclasses to inherit from
   ``celery_haystack.indexes.CelerySearchIndex`` (as well as
   ``haystack.indexes.Indexable``).
3. Ensure your Celery instance is running.

Thanks
------

This app is a blatant rip-off of Daniel Lindsley's queued_search_
app but uses Ask Solem Hoel's Celery_ instead of the equally awesome
queues_ library by Matt Croyden.

.. _queued_search: https://github.com/toastdriven/queued_search/
.. _Celery: http://celeryproject.org/
.. _queues: http://code.google.com/p/queues/
