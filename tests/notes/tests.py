import base64
import pickle

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from celery import current_app

from notes.models import Note


class QueuedSearchIndexTestCase(TestCase):

    def get_or_create_queue(self):
        broker_connection = current_app.broker_connection()
        channel = broker_connection.channel()
        return channel._queue_for(settings.CELERY_DEFAULT_QUEUE)

    def assertArgsInQueue(self, queue, args):
        messages = []
        for item in queue.queue:
            body = item.get('body')
            if body:
                unpickled_body = pickle.loads(base64.b64decode(body))
                unpickled_args = unpickled_body.get('args')
                if unpickled_args:
                    messages.append(unpickled_args)
        self.assertEqual(messages, args)

    def setUp(self):
        # Nuke the index.
        call_command('clear_index', interactive=False, verbosity=0)

        # Throw away all Notes
        Note.objects.all().delete()

        # Get a queue connection so we can poke at it.
        self.queue = self.get_or_create_queue()

        self.queue.queue.clear()

    def test_update(self):
        self.assertEqual(self.queue.qsize(), 0)

        Note.objects.create(
            title='A test note',
            content='Because everyone loves test data.',
            author='Daniel',
        )
        self.assertEqual(self.queue.qsize(), 1)

        Note.objects.create(
            title='Another test note',
            content='More test data.',
            author='Daniel',
        )
        self.assertEqual(self.queue.qsize(), 2)

        note3 = Note.objects.create(
            title='Final test note',
            content='The test data. All done.',
            author='Joe',
        )
        self.assertEqual(self.queue.qsize(), 3)

        note3.title = 'Final test note FOR REAL'
        note3.save()
        self.assertEqual(self.queue.qsize(), 4)

        self.assertArgsInQueue(self.queue, [
            ('update', u'notes.note.1'),
            ('update', u'notes.note.2'),
            ('update', u'notes.note.3'),
            ('update', u'notes.note.3'),
        ])

    def test_delete(self):
        note1 = Note.objects.create(
            title='A test note',
            content='Because everyone loves test data.',
            author='Daniel',
        )
        note2 = Note.objects.create(
            title='Another test note',
            content='More test data.',
            author='Daniel',
        )
        note3 = Note.objects.create(
            title='Final test note',
            content='The test data. All done.',
            author='Joe',
        )

        # Dump the queue in preparation for the deletes.
        self.queue.queue.clear()
        self.assertEqual(self.queue.qsize(), 0)

        note1.delete()
        self.assertEqual(self.queue.qsize(), 1)

        note2.delete()
        self.assertEqual(self.queue.qsize(), 2)

        note3.delete()
        self.assertEqual(self.queue.qsize(), 3)

        self.assertArgsInQueue(self.queue, [
            ('delete', u'notes.note.1'),
            ('delete', u'notes.note.2'),
            ('delete', u'notes.note.3'),
        ])

    def test_complex(self):
        self.assertEqual(self.queue.qsize(), 0)
        note1 = Note.objects.create(
            title='A test note',
            content='Because everyone loves test data.',
            author='Daniel',
        )

        self.assertEqual(self.queue.qsize(), 1)
        Note.objects.create(
            title='Another test note',
            content='More test data.',
            author='Daniel',
        )

        self.assertEqual(self.queue.qsize(), 2)
        note1.delete()
        self.assertEqual(self.queue.qsize(), 3)

        note3 = Note.objects.create(
            title='Final test note',
            content='The test data. All done.',
            author='Joe',
        )
        self.assertEqual(self.queue.qsize(), 4)

        note3.title = 'Final test note FOR REAL'
        note3.save()
        self.assertEqual(self.queue.qsize(), 5)

        note3.delete()
        self.assertEqual(self.queue.qsize(), 6)

        self.assertArgsInQueue(self.queue, [
            ('update', u'notes.note.1'),
            ('update', u'notes.note.2'),
            ('delete', u'notes.note.1'),
            ('update', u'notes.note.3'),
            ('update', u'notes.note.3'),
            ('delete', u'notes.note.3'),
        ])
