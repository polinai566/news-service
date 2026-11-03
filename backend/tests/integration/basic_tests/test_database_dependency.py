import pytest
from fastapi import Depends, FastAPI
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
async def test_fastapi_uses_the_test_database_session(
    db_app: FastAPI,
    db_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Check that FastAPI uses the session provided by pytest."""

    from app.database import get_db_session

    async def database_session_probe(
        session: AsyncSession = Depends(get_db_session),
    ) -> dict[str, int]:
        result = await session.execute(text("SELECT 1"))

        return {
            "query_result": result.scalar_one(),
            "session_id": id(session),
        }

    db_app.add_api_route(
        "/_test/database-session",
        database_session_probe,
        methods=["GET"],
    )

    response = await db_client.get("/_test/database-session")

    assert response.status_code == 200

    assert response.json() == {
        "query_result": 1,
        "session_id": id(db_session),
    }
