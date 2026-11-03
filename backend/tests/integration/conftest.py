import sys
import os
import subprocess
from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from redis.asyncio import Redis
from testcontainers.community.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """Start one PostgreSQL container for the entire test session."""
    with PostgresContainer("postgres:17") as container:
        yield container

@pytest.fixture(scope="session")
def redis_container() -> Iterator[RedisContainer]:
    with RedisContainer("redis:7-alpine") as container:
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

@pytest.fixture(scope="session")
def app_environment(
    migrated_postgres_url: str,
) -> Iterator[None]:
    """Set test environment variables before importing the application."""

    database_url = make_url(migrated_postgres_url)

    test_variables = {
        "POSTGRES_USER": database_url.username or "",
        "POSTGRES_PASSWORD": database_url.password or "",
        "POSTGRES_HOST": database_url.host or "",
        "POSTGRES_DB": database_url.database or "",
        "POSTGRES_PORT": str(database_url.port or ""),
        "HAWK_DSN": "",
    }

    original_variables = {
        key: os.environ.get(key)
        for key in test_variables
    }

    os.environ.update(test_variables)

    try:
        yield
    finally:
        for key, value in original_variables.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

@pytest.fixture(scope="session", autouse=True)
def patched_redis(
    redis_container: RedisContainer,
    app_environment,
) -> Iterator[Redis]:
    """Replace every module-level redis_client with a client pointing at the test container."""

    import app.database

    client = Redis(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        decode_responses=True
    )

    original = app.database.redis_client
    patched: list = []
    for name, module in list(sys.modules.items()):
        if not name.startswith("app.") or module is None:
            continue
        if getattr(module, "redis_client", None) is original:
            module.redis_client = client
            patched.append(module)

    try:
        yield client
    finally:
        for module in patched:
            module.redis_client = original

@pytest.fixture
async def db_connection(
    migrated_postgres_url: str,
) -> AsyncIterator[AsyncConnection]:
    """Provide a connection with an outer transaction for one test."""

    async_database_url = make_url(
        migrated_postgres_url
    ).set(drivername="postgresql+asyncpg")

    engine = create_async_engine(async_database_url)

    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()

            try:
                yield connection
            finally:
                if transaction.is_active:
                    await transaction.rollback()

    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(
    db_connection: AsyncConnection,
) -> AsyncIterator[AsyncSession]:
    """Provide an isolated async SQLAlchemy session for one test."""

    session_factory = async_sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with session_factory() as session:
        yield session

@pytest.fixture
def app(app_environment) -> Iterator[FastAPI]:
    """Create a fresh FastAPI application instance for one test."""

    from app.main import create_app

    application = create_app()

    yield application

@pytest.fixture
def db_app(
    app: FastAPI,
    db_session: AsyncSession,
) -> Iterator[FastAPI]:
    """Override the application's database dependency with a test session."""

    from app.database import get_db_session

    async def override_get_db_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db_session] = (
        override_get_db_session
    )

    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Provide an asynchronous HTTP client for API tests."""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

@pytest.fixture
async def db_client(
    db_app: FastAPI,
) -> AsyncIterator[AsyncClient]:
    """Provide an HTTP client connected to the test database session."""

    transport = ASGITransport(app=db_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client