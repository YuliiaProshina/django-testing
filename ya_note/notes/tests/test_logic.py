from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from .test_utils import TestNote


class TestNoteCreation(TestNote):

    def test_not_authorized_client_cant_add_note(self):
        notes_count_before = Note.objects.count()
        self.client.post(self.add_url,
                         data={'title': 'Заголовок', 'text': 'Текст заметки'})
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_authorized_client_can_add_note(self):
        notes_count_before = Note.objects.count()
        data = {'title': 'Заголовок', 'text': 'Текст заметки'}
        self.author_client.post(self.add_url, data=data)
        notes_count_after = Note.objects.count()
        note = Note.objects.get(title=data['title'])
        self.assertEqual(notes_count_after, notes_count_before + 1)
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.author, self.author)

    def test_notes_slug_dublication_prohibited(self):
        notes_count_before = Note.objects.count()
        data = {'title': 'Заголовок', 'text': 'Текст заметки',
                'slug': 'test_slug'}
        first_response = self.author_client.post(self.add_url, data=data)
        self.assertEqual(first_response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        second_response = self.author_client.post(self.add_url, data=data)
        self.assertEqual(second_response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        form = second_response.context['form']
        self.assertFormError(form=form, field='slug',
                             errors=f'{data['slug']}{WARNING}')

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        self.author_client.post(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_author_can_edit_note(self):
        previuos_note = Note.objects.get(slug=self.note.slug)
        data = {'title': 'New title', 'text': self.note.text,
                'slug': self.note.slug}
        self.author_client.post(self.edit_url, data=data)
        note = Note.objects.get(pk=self.note.pk)
        self.assertNotEqual(previuos_note.title, note.title)
        self.assertEqual(previuos_note.text, note.text)
        self.assertEqual(previuos_note.author, note.author)

    def test_user_cant_delete_another_author_note(self):
        notes_count_before = Note.objects.count()
        self.another_client.post(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_cant_edit_another_author_note(self):
        previuos_note = Note.objects.get(slug=self.note.slug)
        data = {'title': 'New title', 'text': self.note.text,
                'slug': self.note.slug}
        self.another_client.post(self.edit_url, data=data)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(previuos_note.title, note.title)
        self.assertEqual(previuos_note.text, note.text)
        self.assertEqual(previuos_note.author, note.author)

    def test_slug_autocreated_when_no_passed(self):
        notes_before = Note.objects.count()
        data = {'title': 'Заголовок', 'text': 'Текст заметки'}
        self.author_client.post(self.add_url, data=data)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        note = Note.objects.get(author=self.author, title=data['title'])
        self.assertEqual(note.slug, slugify(data['title']))
