import pytest
from sqlalchemy import create_engine, inspect, text


@pytest.mark.integration
def test_alembic_migrations_create_expected_schema_and_clean_seed_data(
    migrated_postgres_url: str,
) -> None:
    """Check that migrations create the schema and seed data is removed."""

    engine = create_engine(migrated_postgres_url)

    expected_tables = {
        "user",
        "news",
        "comment",
        "session",
        "alembic_version",
    }

    try:
        actual_tables = set(inspect(engine).get_table_names())

        with engine.connect() as connection:
            current_revision = connection.scalar(
                text("SELECT version_num FROM alembic_version")
            )

            table_counts = {
                table_name: connection.scalar(
                    text(f'SELECT COUNT(*) FROM "{table_name}"')
                )
                for table_name in ("user", "news", "comment", "session")
            }

        assert expected_tables.issubset(actual_tables)
        assert current_revision == "7f3dabf6fc20"
        assert table_counts == {
            "user": 0,
            "news": 0,
            "comment": 0,
            "session": 0,
        }

    finally:
        engine.dispose()
