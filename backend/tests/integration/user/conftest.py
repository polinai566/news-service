from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User
from app.utils import create_paseto_token


@pytest.fixture
def authorization_headers() -> Callable[..., dict[str, str]]:
    """Create authorization headers with a valid PASETO token."""

    def _authorization_headers(
        user_id: int,
        user_role: str = "user",
    ) -> dict[str, str]:
        token = create_paseto_token(
            user_id=user_id,
            user_role=user_role,
        )

        return {"Authorization": f"Bearer {token}"}

    return _authorization_headers


@pytest.fixture
def create_user(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """Create a user directly in the test database."""

    async def _create_user(
        email: str,
        user_name: str = "existing_user",
        user_role: str = "user",
    ) -> User:
        user = User(
            user_name=user_name,
            email=email,
            user_role=user_role,
            password="test_password_hash",
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        return user

    return _create_user