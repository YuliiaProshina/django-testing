from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_home_availability_for_anonymous_user(client, home_url):
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK


def test_detail_availability_for_anonymous_user(client, detail_url):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url',
    ('home_url', 'login_url', 'signup_url')
)
def test_pages_availability_for_anonymous_user(request, client, reverse_url):
    url = request.getfixturevalue(reverse_url)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability_for_anonymous_user(client, logout_url):
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    (
        ('edit_url', 'not_author_client', HTTPStatus.NOT_FOUND),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'not_author_client', HTTPStatus.NOT_FOUND),
        ('delete_url', 'author_client', HTTPStatus.OK)
    ),
)
def test_pages_availability_for_different_users(
        request, reverse_url, parametrized_client, expected_status
):
    url = request.getfixturevalue(reverse_url)
    client = request.getfixturevalue(parametrized_client)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'reverse_url',
    ('edit_url', 'delete_url',),
)
def test_redirects(request, client, reverse_url, login_url):
    url = request.getfixturevalue(reverse_url)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
