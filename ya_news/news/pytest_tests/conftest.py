import pytest

from news.models import Comment, News
from django.test.client import Client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text='Текст комментария',
        news=news,
        author=author,
    )
    return comment


@pytest.fixture
def news(db):
    return News.objects.create(title="Test title", text="Test text")


@pytest.fixture
def pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
