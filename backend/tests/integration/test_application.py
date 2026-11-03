import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_openapi_schema_is_available(
    client: AsyncClient,
) -> None:
    """Check that the application exposes its OpenAPI schema."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert isinstance(schema.get("paths"), dict)
    assert schema["paths"]
