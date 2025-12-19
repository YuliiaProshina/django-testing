from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestNote(TestCase):
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
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.another_client = cls.client_class()
        cls.another_client.force_login(cls.another_author)
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug, ))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug, ))
        cls.home_url = reverse('notes:home')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug, ))
        cls.login_url = reverse('users:login')
        cls.success_url = reverse('notes:success')
        cls.signup_url = reverse('users:signup')
