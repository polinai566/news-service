import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_get_current_user_profile(
    db_client: AsyncClient,
    create_user,
    authorization_headers,
) -> None:
    """Check that an authenticated user receives their own profile."""

    user = await create_user(
        email="current_user@example.com",
        user_name="current_user",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    response = await db_client.get(
        "/user/me",
        headers=headers,
    )

    assert response.status_code == 200

    profile = response.json()

    assert profile["user_id"] == user.user_id
    assert profile["user_name"] == user.user_name
    assert profile["email"] == user.email
    assert profile["user_role"] == user.user_role
    assert profile["avatar"] == user.avatar
    assert "registration_date" in profile
    assert "password" not in profile

@pytest.mark.integration
async def test_get_current_user_profile_requires_authentication(
    db_client: AsyncClient,
) -> None:
    """Check that an unauthenticated request to /user/me is rejected."""

    response = await db_client.get("/user/me")

    assert response.status_code == 401

@pytest.mark.integration
async def test_get_current_user_profile_returns_not_found_for_nonexistent_user(
    db_client: AsyncClient,
    authorization_headers,
) -> None:
    """Check that a token referencing a nonexistent user returns 404."""

    headers = authorization_headers(
        user_id=999999,
    )

    response = await db_client.get(
        "/user/me",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }
