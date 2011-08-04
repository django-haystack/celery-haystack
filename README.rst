===============
celery-haystack
===============

This Django app allows you to utilize Celery for automatically updating and
deleting objects in a Haystack_ search index.

Requirements
------------

* Django 1.2+
* Haystack_ `1.2.X`_ *or* `2.0.X`_
* Celery_ 1.X

You also need to install your choice of one of the supported search engines
for Haystack and one of the supported backends for Celery.

.. _Haystack: http://haystacksearch.org
.. _`1.2.X`: http://pypi.python.org/pypi/django-haystack/1.2.4
.. _`2.0.X`: https://github.com/toastdriven/django-haystack/tree/master

Installation
------------

Use your favorite Python package manager to install the app from PyPI, e.g.::

    pip install celery-haystack

Setup
-----

1. Add ``'celery_haystack'`` to ``INSTALLED_APPS``.
2. Alter all of your ``SearchIndex`` subclasses to inherit from
   ``celery_haystack.indexes.CelerySearchIndex`` (as well as
   ``haystack.indexes.Indexable``).
3. Ensure your Celery instance is running.

Changelog
---------

0.2 (2011-08-04)
^^^^^^^^^^^^^^^^

* Added support for Haystack 1.2.X.

* Properly stop indexing if instance couldn't be found.

* Forced Celery task config values to be of the correct type.

0.1.2 (2011-07-29) and 0.1.3 (2011-08-01)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Removed stale print statement.

0.1.1 (2011-07-29)
^^^^^^^^^^^^^^^^^^

* Fixed packaging issue (added manifest template).


0.1 (2011-07-29)
^^^^^^^^^^^^^^^^

* Initial release.

Thanks
------

This app is a blatant rip-off of Daniel Lindsley's queued_search_
app but uses Ask Solem Hoel's Celery_ instead of the equally awesome
queues_ library by Matt Croyden.

.. _queued_search: https://github.com/toastdriven/queued_search/
.. _Celery: http://celeryproject.org/
.. _queues: http://code.google.com/p/queues/
