from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db
FORM_DATA = {'text': 'Новый текст'}


def test_user_can_create_comment(author_client, author, news, detail_url):
    Comment.objects.all().delete()
    comment_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comment_count_before + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(client, detail_url, login_url):
    comment_count_before = Comment.objects.count()
    response = client.post(detail_url, data=FORM_DATA)
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


def test_author_can_edit_comment(author_client, comment, edit_url, detail_url):
    response = author_client.post(edit_url, FORM_DATA)
    expected_url = detail_url + '#comments'
    assertRedirects(response, expected_url)
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_other_user_cant_edit_note(not_author_client, comment, author,
                                   edit_url):
    response = not_author_client.post(edit_url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == updated_comment.text
    assert comment.author == updated_comment.author
    assert comment.news == updated_comment.news


def test_author_can_delete_comment(author_client, delete_url, detail_url):
    comment_count_before = Comment.objects.count()
    response = author_client.post(delete_url)
    expected = detail_url + '#comments'
    assertRedirects(response, expected)
    assert Comment.objects.count() == comment_count_before - 1


def test_other_user_cant_delete_comment(not_author_client, delete_url):
    comment_count_before = Comment.objects.count()
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count_before
