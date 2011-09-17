===============
celery-haystack
===============

This Django app allows you to utilize Celery for automatically updating and
deleting objects in a Haystack_ search index.

Requirements
------------

* Django 1.2+
* Haystack_ `1.2.X`_ *or* `2.0.X`_
* Celery_ 2.X

You also need to install your choice of one of the supported search engines
for Haystack and one of the supported backends for Celery.

.. _Haystack: http://haystacksearch.org
.. _`1.2.X`: http://pypi.python.org/pypi/django-haystack/1.2.4
.. _`2.0.X`: https://github.com/toastdriven/django-haystack/tree/master

Installation
------------

Use your favorite Python package manager to install the app from PyPI, e.g.::

    pip install celery-haystack

By default a few dependencies will automatically be installed:

- django-appconf_ -- An app to gracefully handle application settings.

- versiontools_ -- A library to help staying compatible to `PEP 386`_.

.. _django-appconf: http://pypi.python.org/pypi/django-appconf
.. _versiontools: http://pypi.python.org/pypi/versiontools
.. _`PEP 386`: http://www.python.org/dev/peps/pep-0386/

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

Issues
------

Please use the `Github issue tracker`_ for any bug reports or feature
requests.

.. _`Github issue tracker`: https://github.com/ennio/celery-haystack/issues
