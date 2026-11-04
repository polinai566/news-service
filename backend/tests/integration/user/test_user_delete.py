import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User


@pytest.mark.integration
async def test_user_can_delete_own_account(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that a user can delete their own account."""

    user = await create_user(
        email="delete_own@example.com",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    response = await db_client.delete(
        f"/user/{user.user_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == "The user was successfully deleted"

    result = await db_session.execute(
        select(User).where(User.user_id == user.user_id)
    )
    deleted_user = result.scalar_one_or_none()

    assert deleted_user is None


@pytest.mark.integration
async def test_user_cannot_delete_another_users_account(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that a user cannot delete another user's account."""

    target_user = await create_user(
        email="delete_protected@example.com",
    )

    headers = authorization_headers(
        user_id=target_user.user_id + 1,
    )

    response = await db_client.delete(
        f"/user/{target_user.user_id}",
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Permission denied"
    }

    result = await db_session.execute(
        select(User).where(User.user_id == target_user.user_id)
    )
    existing_user = result.scalar_one_or_none()

    assert existing_user is not None
    assert existing_user.email == "delete_protected@example.com"


@pytest.mark.integration
async def test_admin_can_delete_another_users_account(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that an administrator can delete another user's account."""

    target_user = await create_user(
        email="admin_delete_target@example.com",
    )

    headers = authorization_headers(
        user_id=999,
        user_role="admin",
    )

    response = await db_client.delete(
        f"/user/{target_user.user_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == "The user was successfully deleted"

    result = await db_session.execute(
        select(User).where(User.user_id == target_user.user_id)
    )
    deleted_user = result.scalar_one_or_none()

    assert deleted_user is None


@pytest.mark.integration
async def test_delete_nonexistent_user_returns_not_found(
    db_client: AsyncClient,
    authorization_headers,
) -> None:
    """Check that deleting a nonexistent user returns 404."""

    nonexistent_user_id = 999999

    headers = authorization_headers(
        user_id=nonexistent_user_id,
    )

    response = await db_client.delete(
        f"/user/{nonexistent_user_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }


@pytest.mark.integration
async def test_delete_user_requires_authentication(
    db_client: AsyncClient,
) -> None:
    """Check that an unauthenticated delete request is rejected."""

    response = await db_client.delete("/user/123")

    assert response.status_code == 401
