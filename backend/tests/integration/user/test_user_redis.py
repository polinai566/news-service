import json

import pytest
from httpx import AsyncClient
from redis.asyncio import Redis

from app.user.models import User


async def create_redis_session(
    redis_client: Redis,
    user: User,
    refresh_token: str,
) -> str:
    """Create a test Redis session and return its key."""

    key = f"session:{user.user_id}:{refresh_token}"

    session_data = {
        "user_id": user.user_id,
        "user_role": user.user_role,
        "user_agent": "test-user-agent",
        "refresh_token": refresh_token,
        "refresh_token_expiretime": "2099-01-01T00:00:00+00:00",
    }

    await redis_client.setex(
        key,
        3600,
        json.dumps(session_data),
    )

    return key


@pytest.mark.integration
async def test_deleting_user_removes_all_redis_sessions(
    db_client: AsyncClient,
    create_user,
    authorization_headers,
    patched_redis: Redis,
) -> None:
    """Check that deleting a user removes all their Redis sessions."""

    user = await create_user(
        email="redis_delete_user@example.com",
    )
    another_user = await create_user(
        email="redis_delete_another@example.com",
    )

    user_session_keys = [
        await create_redis_session(
            patched_redis,
            user,
            "delete_token_1",
        ),
        await create_redis_session(
            patched_redis,
            user,
            "delete_token_2",
        ),
    ]

    another_user_session_key = await create_redis_session(
        patched_redis,
        another_user,
        "another_user_token",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    all_keys = [*user_session_keys, another_user_session_key]

    try:
        response = await db_client.delete(
            f"/user/{user.user_id}",
            headers=headers,
        )

        assert response.status_code == 200

        assert await patched_redis.exists(*user_session_keys) == 0
        assert await patched_redis.exists(another_user_session_key) == 1

    finally:
        await patched_redis.delete(*all_keys)


@pytest.mark.integration
async def test_updating_user_removes_all_redis_sessions(
    db_client: AsyncClient,
    create_user,
    authorization_headers,
    patched_redis: Redis,
) -> None:
    """Check that updating a user's profile removes all their Redis sessions."""

    user = await create_user(
        email="redis_update_user@example.com",
    )
    another_user = await create_user(
        email="redis_update_another@example.com",
    )

    user_session_keys = [
        await create_redis_session(
            patched_redis,
            user,
            "update_token_1",
        ),
        await create_redis_session(
            patched_redis,
            user,
            "update_token_2",
        ),
    ]

    another_user_session_key = await create_redis_session(
        patched_redis,
        another_user,
        "another_update_user_token",
    )

    headers = authorization_headers(
        user_id=user.user_id,
    )

    payload = {
        "user_name": "updated_name",
        "email": user.email,
    }

    all_keys = [*user_session_keys, another_user_session_key]

    try:
        response = await db_client.put(
            f"/user/{user.user_id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 200

        assert await patched_redis.exists(*user_session_keys) == 0
        assert await patched_redis.exists(another_user_session_key) == 1

    finally:
        await patched_redis.delete(*all_keys)
