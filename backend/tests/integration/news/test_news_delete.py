import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_author_can_delete_own_news_and_cache_is_invalidated(
    db_client: AsyncClient,
    create_author,
    create_news,
    authorization_headers,
) -> None:
    """Check that an author can delete own news and both caches are invalidated."""

    author = await create_author()
    news = await create_news(author)

    headers = authorization_headers(
        user_id=author.user_id,
        user_role="author",
    )

    response = await db_client.get(f"/news/{news.news_id}")
    assert response.status_code == 200

    response = await db_client.get("/news/")
    assert response.status_code == 200

    response = await db_client.delete(
        f"/news/{news.news_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == "The news was successfully deleted"

    response = await db_client.get(f"/news/{news.news_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "News not found"

    response = await db_client.get("/news/")

    assert response.status_code == 200
    assert all(
        item["news_id"] != news.news_id
        for item in response.json()
    )


@pytest.mark.integration
async def test_author_cannot_delete_another_authors_news(
    db_client: AsyncClient,
    create_author,
    create_news,
    authorization_headers,
) -> None:
    """Check that an author cannot delete news belonging to another author."""

    owner = await create_author()
    another_author = await create_author(email="another@example.com")
    news = await create_news(owner)

    headers = authorization_headers(
        user_id=another_author.user_id,
        user_role="author",
    )

    response = await db_client.delete(
        f"/news/{news.news_id}",
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"

    response = await db_client.get(f"/news/{news.news_id}")

    assert response.status_code == 200
    assert response.json()["news_id"] == news.news_id


@pytest.mark.integration
async def test_delete_nonexistent_news_returns_404(
    db_client: AsyncClient,
    create_author,
    authorization_headers,
) -> None:
    """Check that deleting nonexistent news returns 404."""

    author = await create_author()

    headers = authorization_headers(
        user_id=author.user_id,
        user_role="author",
    )

    response = await db_client.delete(
        "/news/999999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "News not found"
