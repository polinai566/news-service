import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
)


@pytest.mark.integration
async def test_db_session_commit_is_rolled_back_with_outer_transaction(
    db_connection: AsyncConnection,
    db_session: AsyncSession,
    migrated_postgres_url: str,
) -> None:
    """Ensure that session.commit() does not commit the outer transaction."""

    test_email = "transaction-rollback@example.test"

    await db_session.execute(
        text(
            'INSERT INTO "user" (user_name, email) '
            'VALUES (:user_name, :email)'
        ),
        {
            "user_name": "transaction_test",
            "email": test_email,
        },
    )

    await db_session.commit()

    assert db_connection.in_transaction()

    await db_connection.rollback()

    async_database_url = make_url(
        migrated_postgres_url
    ).set(drivername="postgresql+asyncpg")

    verification_engine = create_async_engine(async_database_url)

    try:
        async with verification_engine.connect() as connection:
            result = await connection.execute(
                text(
                    'SELECT COUNT(*) FROM "user" '
                    'WHERE email = :email'
                ),
                {"email": test_email},
            )

            user_count = result.scalar_one()

        assert user_count == 0

    finally:
        await verification_engine.dispose()
