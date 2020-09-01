===============
celery-haystack
===============

.. image:: https://secure.travis-ci.org/django-haystack/celery-haystack.png?branch=develop
    :alt: Build Status
    :target: http://travis-ci.org/django-haystack/celery-haystack

This Django app allows you to utilize Celery for automatically updating and
deleting objects in a Haystack_ search index.

Requirements
------------

* Django 1.8+
* Haystack_ `2.X`_
* Celery_ 3.X / 4.X

You also need to install your choice of one of the supported search engines
for Haystack and one of the supported backends for Celery.


.. _Haystack: http://haystacksearch.org
.. _Celery: http://www.celeryproject.org


Installation
------------

Use your favorite Python package manager to install the app from PyPI, e.g.::

    pip install celery-haystack


For Django < 1.9 you need to install and configure `django-transaction-hooks`_ -- an app that
brings transaction commit hooks to Django.

.. _django-transaction-hooks: https://github.com/carljm/django-transaction-hooks


Usage
-----

1. Add ``'celery_haystack'`` to the ``INSTALLED_APPS`` setting

   .. code:: python

     INSTALLED_APPS = [
         # ..
         'celery_haystack',
     ]

2. Enable the celery-haystack signal processor in the settings

   .. code:: python

    HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'

3. Alter all of your ``SearchIndex`` subclasses to inherit from
   ``celery_haystack.indexes.CelerySearchIndex`` and
   ``haystack.indexes.Indexable``

   .. code:: python

     from haystack import indexes
     from celery_haystack.indexes import CelerySearchIndex
     from myapp.models import Note

     class NoteIndex(CelerySearchIndex, indexes.Indexable):
         text = indexes.CharField(document=True, model_attr='content')

         def get_model(self):
             return Note

4. Ensure your Celery instance is running.

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

.. _`Github issue tracker`: https://github.com/django-haystack/celery-haystack/issues
