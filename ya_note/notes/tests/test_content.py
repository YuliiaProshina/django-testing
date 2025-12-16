from notes.models import Note
from notes.forms import NoteForm
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestContent(TestCase):

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

    def test_note_in_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        responce = self.client.get(url)
        self.assertIn(self.note, responce.context['object_list'])

    def test_not_see_another_author_notes(self):
        self.client.force_login(self.another_author)
        url = reverse('notes:list')
        responce = self.client.get(url)
        self.assertNotIn(self.note, responce.context['object_list'])

    def test_authorized_client_has_add_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_edit_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
