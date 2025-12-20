import os

import httpx
import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()
USER = os.environ["POSTGRES_USER"]
PASSWORD = os.environ["POSTGRES_PASSWORD"]
HOST = os.environ["POSTGRES_HOST"]
DB = os.environ["POSTGRES_DB"]
PORT = os.environ["POSTGRES_PORT"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])


DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

BASE_URL = f"http://{HOST}:8000"

# Список login'ов, используемых в тестах
TEST_LOGINS = [
    "test_user_1",
    "duplicate_test",
    "weak",
]


# Удаляет тестовых пользователей из БД
def _clean_test_users():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    for login in TEST_LOGINS:
        cur.execute('DELETE FROM "user" WHERE login = %s', (login,))
    conn.commit()
    cur.close()
    conn.close()


# Очищает тестовые данные перед каждым тестом.
@pytest.fixture(autouse=True)
def clean_db_before_each_test():
    _clean_test_users()
    yield


@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL) as c:
        yield c


# Тест 1: Успешная регистрация
def test_successful_registration(client):
    user_data = {
        "user_name": "test_user_1",
        "login": "test_user_1",
        "is_verified": False,
        "avatar": "default_avatar.png",
        "password": "StrongPassword123!",
    }

    response = client.post("/user/", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert data["login"] == user_data["login"]
    assert "user_name" in data
    assert "avatar" in data
    assert "registration_date" in data


# Тест 2: Дублирующий логин
def test_duplicate_login_registration(client):
    login = "duplicate_test"
    user1 = {
        "user_name": "user1",
        "login": login,
        "is_verified": False,
        "avatar": "a1.png",
        "password": "Pass123!",
    }
    user2 = {
        "user_name": "user2",
        "login": login,
        "is_verified": False,
        "avatar": "a2.png",
        "password": "Pass456!",
    }

    resp1 = client.post("/user/", json=user1)
    assert resp1.status_code == 200

    resp2 = client.post("/user/", json=user2)
    assert resp2.status_code == 409


# Тест 3: Слабый пароль
def test_weak_password_registration(client):
    user_data = {
        "user_name": "weak_user",
        "login": "weak",
        "is_verified": False,
        "avatar": "weak.png",
        "password": "123",
    }

    response = client.post("/user/", json=user_data)

    # Ожидаем ошибку валидации от Pydantic
    assert response.status_code == 422, (
        "Слабый пароль был принят! Ожидался статус 422 (ошибка валидации)."
    )
