import os
import subprocess
from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """Start one PostgreSQL container for the entire test session."""
    with PostgresContainer("postgres:17") as container:
        yield container

@pytest.fixture(scope="session")
def migrated_postgres_url(
    postgres_container: PostgresContainer,
    backend_root,
) -> str:
    """Apply Alembic migrations and prepare a clean test database."""

    database_url = postgres_container.get_connection_url()
    parsed_url = make_url(database_url)

    environment = os.environ.copy()
    environment.update(
        {
            "POSTGRES_USER": parsed_url.username or "",
            "POSTGRES_PASSWORD": parsed_url.password or "",
            "POSTGRES_HOST": parsed_url.host or "",
            "POSTGRES_DB": parsed_url.database or "",
            "POSTGRES_PORT": str(parsed_url.port or ""),
            "REDIS_HOST": "127.0.0.1",
            "REDIS_PORT": "6379",
        }
    )

    migration_process = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=backend_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    if migration_process.returncode != 0:
        raise RuntimeError(
            "Alembic migrations failed.\n"
            f"STDOUT:\n{migration_process.stdout}\n"
            f"STDERR:\n{migration_process.stderr}"
        )

    engine = create_engine(database_url)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    'TRUNCATE TABLE '
                    '"comment", "news", "session", "user" '
                    'RESTART IDENTITY CASCADE'
                )
            )
    finally:
        engine.dispose()

    return database_url

@pytest.fixture
def app() -> Iterator[FastAPI]:
    """Provide the FastAPI application with isolated dependency overrides."""
    from app.main import app as application

    original_dependency_overrides = (
        application.dependency_overrides.copy()
    )

    application.dependency_overrides.clear()

    try:
        yield application
    finally:
        application.dependency_overrides.clear()
        application.dependency_overrides.update(
            original_dependency_overrides
        )


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Provide an asynchronous HTTP client for API tests."""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client
