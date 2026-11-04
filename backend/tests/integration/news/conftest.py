from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User
from app.news.models import News


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

@pytest.fixture
def create_news(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[News]]:
    """Create a news record directly in the test database."""

    async def _create_news(
        author: User,
        header: str = "Test news",
        content: dict | None = None,
        cover: str | None = None,
    ) -> News:
        news = News(
            header=header,
            content=content or {"text": "This is the content of a test news."},
            cover=cover,
            author_id=author.user_id,
        )

        db_session.add(news)
        await db_session.commit()
        await db_session.refresh(news)
        return news

    return _create_news
