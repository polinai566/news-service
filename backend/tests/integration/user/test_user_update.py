import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import check_password


@pytest.mark.integration
async def test_user_can_update_own_profile(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that a user can update their own profile data."""

    user = await create_user(
        email="update_user@example.com",
        user_name="old_name",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    payload = {
        "user_name": "new_name",
        "email": "updated_email@example.com",
        "avatar": "https://example.com/avatar.png",
    }

    response = await db_client.put(
        f"/user/{user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": user.user_id}
    await db_session.refresh(user)
    assert user.user_name == payload["user_name"]
    assert user.email == payload["email"]
    assert user.avatar == payload["avatar"]
    assert user.user_role == "user"


@pytest.mark.integration
async def test_user_cannot_update_profile_with_existing_email(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that updating a profile with another user's email is rejected."""

    target_user = await create_user(
        email="update_target@example.com",
        user_name="target_user",
    )
    existing_user = await create_user(
        email="existing_email@example.com",
    )

    headers = authorization_headers(
        user_id=target_user.user_id,
    )

    payload = {
        "user_name": "changed_name",
        "email": existing_user.email,
    }

    response = await db_client.put(
        f"/user/{target_user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Email already registered"
    }
    await db_session.refresh(target_user)
    assert target_user.user_name == "target_user"
    assert target_user.email == "update_target@example.com"


@pytest.mark.integration
async def test_user_can_update_password_and_password_is_hashed(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that a new password is securely hashed during profile update."""

    user = await create_user(
        email="password_update@example.com",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    new_password = "new_secure_password"

    payload = {
        "user_name": user.user_name,
        "email": user.email,
        "password": new_password,
    }

    response = await db_client.put(
        f"/user/{user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    await db_session.refresh(user)
    assert user.password != new_password
    assert check_password(new_password, user.password)


@pytest.mark.integration
async def test_empty_password_does_not_change_existing_password(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that an empty password is ignored during profile update."""

    user = await create_user(
        email="empty_password@example.com",
    )
    original_password = user.password

    headers = authorization_headers(
        user_id=user.user_id,
    )

    payload = {
        "user_name": user.user_name,
        "email": user.email,
        "password": "",
    }

    response = await db_client.put(
        f"/user/{user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    await db_session.refresh(user)
    assert user.password == original_password


@pytest.mark.integration
async def test_user_cannot_update_another_users_profile(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that a user cannot update another user's profile."""

    target_user = await create_user(
        email="protected_user@example.com",
        user_name="protected_user",
    )

    headers = authorization_headers(
        user_id=target_user.user_id + 1,
    )

    payload = {
        "user_name": "hacked_name",
        "email": "hacked@example.com",
    }

    response = await db_client.put(
        f"/user/{target_user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 403
    await db_session.refresh(target_user)
    assert target_user.user_name == "protected_user"
    assert target_user.email == "protected_user@example.com"

@pytest.mark.integration
async def test_update_nonexistent_user_returns_not_found(
    db_client: AsyncClient,
    authorization_headers,
) -> None:
    """Check that updating a nonexistent user returns 404."""

    user_id = 999999

    headers = authorization_headers(
        user_id=user_id,
    )

    payload = {
        "user_name": "new_name",
        "email": "missing_user@example.com",
    }

    response = await db_client.put(
        f"/user/{user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }
