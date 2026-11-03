import pytest
from sqlalchemy import create_engine, text
from testcontainers.community.postgres import PostgresContainer


@pytest.mark.integration
def test_postgres_container_starts_and_accepts_connections(
    postgres_container: PostgresContainer,
) -> None:
    """Check that PostgreSQL starts and accepts database connections."""

    database_url = postgres_container.get_connection_url()
    engine = create_engine(database_url)

    try:
        with engine.connect() as connection:
            server_version = connection.execute(
                text("SHOW server_version")
            ).scalar_one()

        assert server_version.split(".", maxsplit=1)[0] == "17"

    finally:
        engine.dispose()
