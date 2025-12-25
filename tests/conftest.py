import pytest
from app.main import create_app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def app():
    return create_app()

@pytest.fixture(scope="session")
def client(app):
    return TestClient(app)

@pytest.fixture
def test_user_dict():
    # пример мок-словаря тестового пользователя
    return {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }

