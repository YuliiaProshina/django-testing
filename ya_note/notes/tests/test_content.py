from notes.forms import NoteForm

from .test_utils import TestNote


class TestContent(TestNote):

    def test_note_in_list(self):
        responce = self.author_client.get(self.list_url)
        self.assertIn(self.note, responce.context['object_list'])

    def test_not_see_another_author_notes(self):
        responce = self.another_client.get(self.list_url)
        self.assertNotIn(self.note, responce.context['object_list'])

    def test_authorized_client_has_add_form(self):
        response = self.author_client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_edit_form(self):
        response = self.author_client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
