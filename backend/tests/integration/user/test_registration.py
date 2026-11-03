import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User
from app.utils import check_password

@pytest.mark.integration
async def test_register_user_creates_user_and_hashes_password(
    db_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Check that registration creates a user and securely stores the password."""

    payload = {
        "user_name": "test_user",
        "email": "test_user@example.com",
        "password": "test_password",
    }

    response = await db_client.post("/user/", json=payload)

    assert response.status_code == 200

    response_data = response.json()

    assert set(response_data) == {"user_id"}
    assert isinstance(response_data["user_id"], int)

    result = await db_session.execute(
        select(User).where(User.user_id == response_data["user_id"])
    )
    user = result.scalar_one()

    assert user.user_name == payload["user_name"]
    assert user.email == payload["email"]
    assert user.user_role == "user"

    assert user.password is not None
    assert user.password != payload["password"]
    assert check_password(payload["password"], user.password)

@pytest.mark.integration
async def test_register_user_with_existing_email_returns_conflict(
    db_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Check that registration with an existing email is rejected."""

    payload = {
        "user_name": "test_user",
        "email": "test_user@example.com",
        "password": "test_password",
    }

    first_response = await db_client.post("/user/", json=payload)

    assert first_response.status_code == 200

    second_response = await db_client.post("/user/", json=payload)

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Email already registered"
    }

    result = await db_session.execute(
        select(User).where(User.email == payload["email"])
    )
    users = result.scalars().all()

    assert len(users) == 1

@pytest.mark.integration
@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        (
            {
                "user_name": "test_user",
                "email": "invalid-email",
                "password": "test_password",
            },
            "email",
        ),
        (
            {
                "email": "missing_name@example.com",
                "password": "test_password",
            },
            "user_name",
        ),
    ],
)
async def test_registration_rejects_invalid_payload(
    db_client: AsyncClient,
    payload: dict[str, str],
    expected_field: str,
) -> None:
    """Check that registration rejects invalid input data."""

    response = await db_client.post("/user/", json=payload)

    assert response.status_code == 422

    errors = response.json()["detail"]
    error_fields = {error["loc"][-1] for error in errors}

    assert expected_field in error_fields

@pytest.mark.integration
async def test_register_user_cannot_assign_admin_role(
    db_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Check that a user cannot assign the admin role during registration."""

    payload = {
        "user_name": "test_user",
        "email": "test_user@example.com",
        "password": "test_password",
        "user_role": "admin",
    }

    response = await db_client.post("/user/", json=payload)

    assert response.status_code == 200

    user_id = response.json()["user_id"]

    result = await db_session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one()

    assert user.user_role == "user"
