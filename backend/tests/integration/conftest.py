from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


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
