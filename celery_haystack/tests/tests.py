from django.core.management import call_command
from django.test import TestCase

from haystack.query import SearchQuerySet

from .models import Note


class QueuedSearchIndexTestCase(TestCase):

    def assertSearchResultLength(self, count):
        self.assertEqual(count, len(SearchQuerySet()))

    def assertSearchResultContains(self, pk, text):
        results = SearchQuerySet().filter(id='tests.note.%s' % pk)
        self.assertTrue(results)
        self.assertTrue(text in results[0].text)

    def setUp(self):
        # Nuke the index.
        call_command('clear_index', interactive=False, verbosity=0)

        # Throw away all Notes
        Note.objects.all().delete()

    def test_update(self):
        self.assertSearchResultLength(0)
        note1 = Note.objects.create(content='Because everyone loves tests.')
        self.assertSearchResultLength(1)
        self.assertSearchResultContains(note1.pk, 'loves')

        note2 = Note.objects.create(content='More test data.')
        self.assertSearchResultLength(2)
        self.assertSearchResultContains(note2.pk, 'More')

        note3 = Note.objects.create(content='The test data. All done.')
        self.assertSearchResultLength(3)
        self.assertSearchResultContains(note3.pk, 'All done')

        note3.content = 'Final test note FOR REAL'
        note3.save()
        self.assertSearchResultLength(3)
        self.assertSearchResultContains(note3.pk, 'FOR REAL')

    def test_delete(self):
        note1 = Note.objects.create(content='Because everyone loves tests.')
        note2 = Note.objects.create(content='More test data.')
        note3 = Note.objects.create(content='The test data. All done.')
        self.assertSearchResultLength(3)
        note1.delete()
        self.assertSearchResultLength(2)
        note2.delete()
        self.assertSearchResultLength(1)
        note3.delete()
        self.assertSearchResultLength(0)

    def test_complex(self):
        note1 = Note.objects.create(content='Because everyone loves test.')
        self.assertSearchResultLength(1)

        Note.objects.create(content='More test data.')
        self.assertSearchResultLength(2)
        note1.delete()
        self.assertSearchResultLength(1)

        note3 = Note.objects.create(content='The test data. All done.')
        self.assertSearchResultLength(2)

        note3.title = 'Final test note FOR REAL'
        note3.save()
        self.assertSearchResultLength(2)

        note3.delete()
        self.assertSearchResultLength(1)
