import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.news.models import News


@pytest.mark.integration
async def test_author_can_create_news_and_notification_is_enqueued(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_author,
    authorization_headers,
    mocker,
) -> None:
    """Check that creating news enqueues a notification task."""

    author = await create_author()
    headers = authorization_headers(
        user_id=author.user_id,
        user_role="author",
    )

    send_task_mock = mocker.patch(
        "app.news.service.task.send_notification_of_new_news"
    )

    payload = {
        "header": "Test news",
        "content": {"text": "News content"},
        "cover": None,
    }

    response = await db_client.post(
        "/news/",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200

    news_id = response.json()["news_id"]

    assert isinstance(news_id, int)

    created_news = await db_session.get(News, news_id)

    assert created_news is not None
    assert created_news.header == payload["header"]
    assert created_news.author_id == author.user_id

    send_task_mock.delay.assert_called_once_with(news_id)


@pytest.mark.integration
async def test_create_news_invalidates_news_list_cache(
    db_client: AsyncClient,
    create_author,
    create_news,
    authorization_headers,
    patched_redis: Redis,
    mocker,
) -> None:
    """Check that creating news invalidates the cached news list."""

    await patched_redis.delete("news_list_all")

    author = await create_author()
    first_news = await create_news(author)

    response = await db_client.get("/news/")

    assert response.status_code == 200
    assert len(response.json()) == 1

    send_task_mock = mocker.patch(
        "app.news.service.task.send_notification_of_new_news"
    )

    headers = authorization_headers(
        user_id=author.user_id,
        user_role="author",
    )

    response = await db_client.post(
        "/news/",
        json={
            "header": "Second news",
            "content": {"text": "Second news content"},
        },
        headers=headers,
    )

    assert response.status_code == 200
    second_news_id = response.json()["news_id"]
    send_task_mock.delay.assert_called_once_with(second_news_id)
    response = await db_client.get("/news/")
    assert response.status_code == 200
    news_list = response.json()

    assert len(news_list) == 2
    assert {item["news_id"] for item in news_list} == {
        first_news.news_id,
        second_news_id,
    }
