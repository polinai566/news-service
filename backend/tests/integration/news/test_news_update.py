import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_author_can_update_own_news_and_cache_is_invalidated(
    db_client: AsyncClient,
    create_author,
    create_news,
    authorization_headers,
) -> None:
    """Check that an author can update own news and both caches are invalidated."""

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

    payload = {
        "header": "Updated news",
        "content": {"text": "Updated content"},
        "cover": "updated-cover.jpg",
    }

    response = await db_client.put(
        f"/news/{news.news_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {"news_id": news.news_id}

    response = await db_client.get(f"/news/{news.news_id}")

    assert response.status_code == 200
    assert response.json()["header"] == payload["header"]
    assert response.json()["content"] == payload["content"]
    assert response.json()["cover"] == payload["cover"]

    response = await db_client.get("/news/")

    assert response.status_code == 200
    updated_news = next(
        item for item in response.json()
        if item["news_id"] == news.news_id
    )
    assert updated_news["header"] == payload["header"]


@pytest.mark.integration
async def test_author_cannot_update_another_authors_news(
    db_client: AsyncClient,
    create_author,
    create_news,
    authorization_headers,
) -> None:
    """Check that an author cannot update news belonging to another author."""

    owner = await create_author()
    another_author = await create_author(email="another@example.com")
    news = await create_news(owner)

    headers = authorization_headers(
        user_id=another_author.user_id,
        user_role="author",
    )

    response = await db_client.put(
        f"/news/{news.news_id}",
        json={
            "header": "Updated news",
            "content": {"text": "Updated content"},
        },
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.integration
async def test_update_nonexistent_news_returns_404(
    db_client: AsyncClient,
    create_author,
    authorization_headers,
) -> None:
    """Check that updating nonexistent news returns 404."""

    author = await create_author()
    headers = authorization_headers(
        user_id=author.user_id,
        user_role="author",
    )

    response = await db_client.put(
        "/news/999999",
        json={
            "header": "Updated news",
            "content": {"text": "Updated content"},
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "News not found"
