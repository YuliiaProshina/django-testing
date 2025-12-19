from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_utils import TestNote


class TestNoteCreation(TestNote):

    def test_not_authorized_client_cant_add_note(self):
        notes_count_before = Note.objects.count()
        self.client.post(self.add_url,
                         data={'title': 'Заголовок', 'text': 'Текст заметки'})
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_authorized_client_can_add_note(self):
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        data = {'title': 'Заголовок', 'text': 'Текст заметки'}
        self.author_client.post(self.add_url, data=data)
        notes_count_after = Note.objects.count()
        note = Note.objects.get()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.author, self.author)

    def test_notes_slug_dublication_prohibited(self):
        notes_count_before = Note.objects.count()
        note = Note.objects.get()
        second_response = self.author_client.post(self.add_url, data={
            'title': self.note.title, 'text': self.note.text,
            'slug': self.note.slug})
        self.assertEqual(second_response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), notes_count_before)
        form = second_response.context['form']
        self.assertFormError(form=form, field='slug',
                             errors=f'{note.slug}{WARNING}')

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        self.author_client.post(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_author_can_edit_note(self):
        data = {'title': 'New title', 'text': 'New text',
                'slug': 'new-slug'}
        self.author_client.post(self.edit_url, data=data)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertNotEqual(self.note.title, updated_note.title)
        self.assertNotEqual(self.note.text, updated_note.text)
        self.assertNotEqual(self.note.slug, updated_note.slug)
        self.assertEqual(updated_note.title, data['title'])
        self.assertEqual(updated_note.text, data['text'])
        self.assertEqual(updated_note.slug, data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cant_delete_another_author_note(self):
        notes_count_before = Note.objects.count()
        self.another_client.post(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_cant_edit_another_author_note(self):
        data = {'title': 'New title', 'text': 'New text',
                'slug': 'new-slug'}
        self.another_client.post(self.edit_url, data=data)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)

    def test_slug_autocreated_when_no_passed(self):
        Note.objects.all().delete()
        notes_before = Note.objects.count()
        data = {'title': 'Заголовок', 'text': 'Текст заметки'}
        self.author_client.post(self.add_url, data=data)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(data['title']))
