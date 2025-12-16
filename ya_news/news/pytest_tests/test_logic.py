from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse
from news.forms import WARNING, BAD_WORDS
from news.models import Comment
from http import HTTPStatus


def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_words_data)
    data = response.context['form']
    assertFormError(data, 'text', WARNING)
    assert response.status_code == HTTPStatus.OK


def test_author_can_edit_comment(author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.post(url, form_data)
    expected_url = reverse('news:detail',
                           args=(comment.news.pk,)) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_note(not_author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    expected = reverse('news:detail', args=(news.pk,)) + '#comments'
    assertRedirects(response, expected)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
