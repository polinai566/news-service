import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
async def test_regular_user_cannot_update_user_role_through_admin_route(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that a regular user cannot change another user's role."""

    target_user = await create_user(
        email="admin_route_target@example.com",
    )

    headers = authorization_headers(
        user_id=target_user.user_id + 1,
        user_role="user",
    )

    payload = {
        "user_name": target_user.user_name,
        "email": target_user.email,
        "user_role": "admin",
    }

    response = await db_client.put(
        f"/user/admin/{target_user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 403
    await db_session.refresh(target_user)
    assert target_user.user_role == "user"


@pytest.mark.integration
async def test_admin_can_update_another_user_role(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that an administrator can change another user's role."""

    target_user = await create_user(
        email="admin_update_target@example.com",
    )

    headers = authorization_headers(
        user_id=999,
        user_role="admin",
    )

    payload = {
        "user_name": target_user.user_name,
        "email": target_user.email,
        "user_role": "author",
    }

    response = await db_client.put(
        f"/user/admin/{target_user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    await db_session.refresh(target_user)
    assert target_user.user_role == "author"


@pytest.mark.integration
async def test_admin_cannot_assign_invalid_user_role(
    db_client: AsyncClient,
    db_session: AsyncSession,
    create_user,
    authorization_headers,
) -> None:
    """Check that an invalid user role is rejected."""

    target_user = await create_user(
        email="invalid_role_target@example.com",
    )

    headers = authorization_headers(
        user_id=999,
        user_role="admin",
    )

    payload = {
        "user_name": target_user.user_name,
        "email": target_user.email,
        "user_role": "superadmin",
    }

    response = await db_client.put(
        f"/user/admin/{target_user.user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 422
    await db_session.refresh(target_user)
    assert target_user.user_role == "user"
