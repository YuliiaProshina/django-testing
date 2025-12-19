from http import HTTPStatus

from .test_utils import TestNote


class TestRoutes(TestNote):

    def test_home_page(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.another_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in (self.edit_url, self.delete_url):
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_detail_available_for_any_user(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.another_client, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            with self.subTest(user=user, status=status):
                response = user.get(self.detail_url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        for url in (self.edit_url, self.delete_url, self.detail_url,
                    self.list_url, self.add_url, self.success_url):
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_add_and_success_and_list(self):
        for url in (self.list_url, self.add_url, self.success_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_all_login_and_logout_and_signup(self):
        for url in (self.login_url, self.signup_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
