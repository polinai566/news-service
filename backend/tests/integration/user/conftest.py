from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User


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