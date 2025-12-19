from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

pytestmark = pytest.mark.django_db
FORM_DATA = {'text': 'Новый текст'}


def test_user_can_create_comment(author_client, author, news, detail_url):
    comment_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comment_count_before + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(client, detail_url):
    comment_count_before = Comment.objects.count()
    response = client.post(detail_url, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comment_count_before


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    response = author_client.post(detail_url, data={'text': f'''Какой-то текст,
                                                     {bad_word}, еще текст'''})
    data = response.context['form']
    assertFormError(data, 'text', WARNING)
    assert response.status_code == HTTPStatus.OK


def test_author_can_edit_comment(author_client, comment, author, edit_url):
    response = author_client.post(edit_url, FORM_DATA)
    expected_url = reverse('news:detail',
                           args=(comment.news.pk,)) + '#comments'
    assertRedirects(response, expected_url)
    comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == FORM_DATA['text']
    assert comment.author == author


def test_other_user_cant_edit_note(not_author_client, comment, author,
                                   edit_url):
    response = not_author_client.post(edit_url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_from_db.text
    assert comment.author == author


def test_author_can_delete_comment(author_client, delete_url, news):
    comment_count_before = Comment.objects.count()
    response = author_client.post(delete_url)
    expected = reverse('news:detail', args=(news.pk,)) + '#comments'
    assertRedirects(response, expected)
    assert Comment.objects.count() == comment_count_before - 1


def test_other_user_cant_delete_comment(not_author_client, delete_url):
    comment_count_before = Comment.objects.count()
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count_before
