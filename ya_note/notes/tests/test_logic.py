from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.another_author = User.objects.create(username='Александр Пушкин')
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='test-slug',
            author=cls.author,
        )

    def test_not_authorized_client_cant_add_note(self):
        notes_count_before = Note.objects.count()
        self.client.post(reverse('notes:add'),
                         data={'title': 'Заголовок', 'text': 'Текст заметки'})
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_authorized_client_can_add_note(self):
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        self.client.post(reverse('notes:add'),
                         data={'title': 'Заголовок', 'text': 'Текст заметки'})
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)

    def test_notes_slug_dublication_prohibited(self):
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        self.client.post(reverse('notes:add'),
                         data={'title': 'Заголовок', 'text': 'Текст заметки'})
        self.client.post(reverse('notes:add'),
                         data={'title': 'Заголовок', 'text': 'Текст заметки'})
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)

    def test_slug_autocreated_when_no_passed(self):
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'),
                         data={'title': 'Заголовок', 'text': 'Текст заметки'})
        note = Note.objects.get(title='Заголовок')
        self.assertEqual(note.slug, slugify('Заголовок'))

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        self.client.post(reverse('notes:delete', args=(self.note.slug, )))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        self.client.post(reverse('notes:edit', args=(self.note.slug, )),
                         data={'title': 'New title', 'text': self.note.text,
                               'slug': self.note.slug})
        note = Note.objects.get(slug=self.note.slug)
        self.assertEqual(note.title, 'New title')

    def test_user_cant_delete_another_author_note(self):
        self.client.force_login(self.another_author)
        notes_count_before = Note.objects.count()
        self.client.post(reverse('notes:delete', args=(self.note.slug, )))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_cant_edit_another_author_note(self):
        self.client.force_login(self.another_author)
        self.client.post(reverse('notes:edit', args=(self.note.slug, )),
                         data={'title': 'New title', 'text': self.note.text,
                               'slug': self.note.slug})
        note = Note.objects.get(slug=self.note.slug)
        self.assertEqual(note.title, note.title)
