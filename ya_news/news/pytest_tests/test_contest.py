import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from news.models import News, Comment

User = get_user_model()


@pytest.mark.django_db
def test_home_news_count(client):
    url = reverse('news:home')
    all_news = [
        News(title=f'Новость {i}', text='Просто текст.')
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_news_order(client):
    url = reverse('news:home')
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {i}',
            text='Просто текст',
            date=today - timedelta(days=i),
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_detail_comments_order(client):
    news = News.objects.create(title='Тестовая новость', text='Просто текст')
    url = reverse('news:detail', args=(news.pk,))
    author = User.objects.create(username='Автор')
    now = timezone.now()
    for i in range(10):
        comment = Comment.objects.create(news=news, author=author,
                                         text=f'Текст {i}')
        comment.created = now + timedelta(days=i)
        comment.save()
    response = client.get(url)
    assert 'news' in response.context
    news_from_context = response.context['news']
    all_comments = news_from_context.comment_set.all()
    timestamps = [c.created for c in all_comments]
    assert timestamps == sorted(timestamps)


@pytest.mark.django_db
def test_detail_anonymous_client_has_no_form(client):
    news = News.objects.create(title='Тестовая новость', text='Просто текст')
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'form' not in response.context
