import pytest
from httpx import AsyncClient
from redis.asyncio import Redis


@pytest.mark.integration
async def test_get_empty_news_list_returns_empty_list(
    db_client: AsyncClient,
    patched_redis: Redis,
) -> None:
    """Check that an empty database results in an empty news list."""

    await patched_redis.delete("news_list_all")
    response = await db_client.get("/news/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
async def test_get_news_list_returns_news_and_uses_cache(
    db_client: AsyncClient,
    create_author,
    create_news,
    patched_redis: Redis,
) -> None:
    """Check that the news list is returned and subsequent requests use the cache."""

    await patched_redis.delete("news_list_all")

    author = await create_author()
    first_news = await create_news(
        author=author,
        header="First news",
    )

    response = await db_client.get("/news/")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    news_data = response_data[0]

    assert news_data["news_id"] == first_news.news_id
    assert news_data["header"] == first_news.header
    assert news_data["content"] == first_news.content
    assert news_data["author_id"] == author.user_id
    assert news_data["author"]["user_id"] == author.user_id

    await create_news(
        author=author,
        header="Second news",
    )

    cached_response = await db_client.get("/news/")
    assert cached_response.status_code == 200
    cached_news = cached_response.json()

    assert len(cached_news) == 1
    assert cached_news[0]["news_id"] == first_news.news_id
