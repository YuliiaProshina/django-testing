from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from news.models import Comment, News

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_home_news_count(client, home_url, all_news):
    News.objects.bulk_create(all_news)
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_home_news_order(client, home_url, all_news):
    News.objects.bulk_create(all_news)
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_detail_comments_order(client, detail_url, news, author):
    for i in range(10):
        comment = Comment.objects.create(news=news, author=author,
                                         text=f'Текст {i}')
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()
    response = client.get(detail_url)
    assert 'news' in response.context
    news_from_context = response.context['news']
    all_comments = news_from_context.comment_set.all()
    timestamps = [c.created for c in all_comments]
    assert timestamps == sorted(timestamps)


def test_detail_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_autorized_client_can_create_comment(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
