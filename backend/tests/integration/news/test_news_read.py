import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.news.models import News


@pytest.mark.integration
async def test_get_news_by_id_returns_news_with_author(
    db_client: AsyncClient,
    create_author,
    create_news,
) -> None:
    """Check that a news item can be retrieved with its author data."""

    author = await create_author()
    news = await create_news(
        author=author,
        header="Integration test news"
    )

    response = await db_client.get(f"/news/{news.news_id}")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["news_id"] == news.news_id
    assert response_data["header"] == news.header
    assert response_data["content"] == news.content
    assert response_data["author_id"] == author.user_id

    assert response_data["author"]["user_id"] == author.user_id
    assert response_data["author"]["user_name"] == author.user_name
    assert response_data["author"]["email"] == author.email
    assert response_data["author"]["user_role"] == "author"

    assert "publication_date" in response_data
    assert "registration_date" in response_data["author"]


@pytest.mark.integration
async def test_get_nonexistent_news_returns_not_found(
    db_client: AsyncClient,
) -> None:
    """Check that requesting a nonexistent news item returns 404."""

    news_id = 999999999

    response = await db_client.get(f"/news/{news_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "News not found"
    }


@pytest.mark.integration
async def test_get_news_by_id_returns_cached_news(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_author,
    create_news,
) -> None:
    """Check that a cached news item is returned without querying the database."""

    author = await create_author()
    news = await create_news(
        author=author,
        header="Original header",
    )

    response = await db_client.get(f"/news/{news.news_id}")

    assert response.status_code == 200
    assert response.json()["header"] == "Original header"

    await db_session.execute(
        update(News)
        .where(News.news_id == news.news_id)
        .values(header="Updated directly in database")
    )
    await db_session.commit()

    response = await db_client.get(f"/news/{news.news_id}")

    assert response.status_code == 200
    assert response.json()["header"] == "Original header"
