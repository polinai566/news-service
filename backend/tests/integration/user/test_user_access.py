import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.integration
async def test_get_user_by_id_requires_authentication(
    db_client: AsyncClient,
) -> None:
    """Check that an unauthenticated request is rejected."""

    response = await db_client.get("/user/123")

    assert response.status_code == 401

@pytest.mark.integration
async def test_user_cannot_get_another_users_profile(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user, authorization_headers
) -> None:
    """Check that users cannot access another user's profile."""

    target_user = await create_user(
        email="target@example.com",
    )

    headers = authorization_headers(
        user_id=target_user.user_id + 1,
    )

    response = await db_client.get(
        f"/user/{target_user.user_id}",
        headers=headers,
    )

    assert response.status_code == 403

@pytest.mark.integration
async def test_regular_user_cannot_get_users_list(
    db_client: AsyncClient,
    authorization_headers
) -> None:
    """Check that only administrators can list all users."""

    headers = authorization_headers(
        user_id=123,
        user_role="user",
    )

    response = await db_client.get(
        "/user/",
        headers=headers,
    )

    assert response.status_code == 403

@pytest.mark.integration
async def test_admin_can_get_users_list(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user, authorization_headers
) -> None:
    """Check that an administrator can retrieve all users."""

    user = await create_user(
        email="listed_user@example.com",
    )

    headers = authorization_headers(
        user_id=999,
        user_role="admin",
    )

    response = await db_client.get(
        "/user/",
        headers=headers,
    )

    assert response.status_code == 200

    users = response.json()

    assert len(users) == 1
    assert users[0]["user_id"] == user.user_id

@pytest.mark.integration
async def test_get_nonexistent_user_returns_not_found(
    db_client: AsyncClient,
    authorization_headers
) -> None:
    """Check that requesting a nonexistent user returns 404."""

    headers = authorization_headers(
        user_id=999,
        user_role="admin",
    )

    response = await db_client.get(
        "/user/999999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }

@pytest.mark.integration
async def test_admin_get_empty_users_list_returns_not_found(
    db_client: AsyncClient,
    authorization_headers,
) -> None:
    """Check that an empty users list returns 404."""

    headers = authorization_headers(
        user_id=999,
        user_role="admin",
    )

    response = await db_client.get(
        "/user/",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "No users found"
    }
