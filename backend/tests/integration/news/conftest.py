from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User


@pytest.fixture
def create_author(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """Create an author directly in the test database."""

    async def _create_author(
        email: str = "author@example.com",
    ) -> User:
        author = User(
            user_name="test_author",
            email=email,
            user_role="author",
            password="test_password_hash",
        )

        db_session.add(author)
        await db_session.commit()
        await db_session.refresh(author)

        return author

    return _create_author