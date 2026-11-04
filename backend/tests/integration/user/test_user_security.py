import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
async def test_user_cannot_see_password_hash_in_own_profile(
    db_client: AsyncClient,
    create_user,
    authorization_headers,
) -> None:
    """Check that a user's own profile does not expose password hash."""

    user = await create_user(
        email="own_profile@example.com",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    response = await db_client.get(
        f"/user/{user.user_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert "password" not in response.json()


@pytest.mark.integration
async def test_admin_cannot_see_password_hash_in_user_profile(
    db_client: AsyncClient,
    create_user,
    authorization_headers,
) -> None:
    """Check that an administrator cannot see another user's password hash."""

    user = await create_user(
        email="admin_view@example.com",
    )

    headers = authorization_headers(
        user_id=999,
        user_role="admin",
    )

    response = await db_client.get(
        f"/user/{user.user_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert "password" not in response.json()


@pytest.mark.integration
async def test_admin_cannot_see_password_hash_in_users_list(
    db_client: AsyncClient,
    create_user,
    authorization_headers,
) -> None:
    """Check that the users list does not expose password hashes."""

    await create_user(
        email="first_user@example.com",
    )
    await create_user(
        email="second_user@example.com",
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

    assert len(users) == 2
    assert all("password" not in user for user in users)

@pytest.mark.integration
async def test_user_cannot_assign_admin_role_to_own_profile(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that a user cannot assign the admin role to their own profile."""

    user = await create_user(
        email="role_update@example.com",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    payload = {
        "user_name": user.user_name,
        "email": user.email,
        "user_role": "admin",
    }

    response = await db_client.put(
        f"/user/{user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200

    await db_session.refresh(user)

    assert user.user_role == "user"
