import os
import asyncio
import psycopg2
import pytest
from httpx import AsyncClient
import redis
from dotenv import load_dotenv
from app.main import create_app

load_dotenv()

ASYNC_DATABASE_URL = os.environ["ASYNC_DATABASE_URL"]
SYNC_DATABASE_URL = os.environ["SYNC_DATABASE_URL"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])

BASE_URL = "http://localhost:8000"

# список тестовых email
TEST_EMAILS = [
    "test@example.com",
    "author@test.com",
    "admin@test.com",
    "user@test.com"
]

# очистка тестовых данных из БД и Redis
def clean_test_data():
    # очистка Redis
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    
    conn = psycopg2.connect(SYNC_DATABASE_URL)
    cur = conn.cursor()
    
    # получение ID тестовых пользователей
    email_placeholders = ','.join(['%s'] * len(TEST_EMAILS))
    cur.execute(f'SELECT user_id FROM "user" WHERE email IN ({email_placeholders})', TEST_EMAILS)
    test_user_ids = [row[0] for row in cur.fetchall()] if cur.rowcount > 0 else []
    
    # удаление сессии тестовых пользователей из Redis
    for user_id in test_user_ids:
        keys = redis_client.keys(f"session:{user_id}:*")
        if keys:
            redis_client.delete(*keys)
    
    # удаление комментариев тестовых пользователей
    if test_user_ids:
        user_id_placeholders = ','.join(['%s'] * len(test_user_ids))
        cur.execute(f'DELETE FROM comment WHERE author_id IN ({user_id_placeholders})', test_user_ids)
    
    # удаление только новости, созданные тестовыми пользователями
    if test_user_ids:
        user_id_placeholders = ','.join(['%s'] * len(test_user_ids))
        cur.execute(f'DELETE FROM news WHERE author_id IN ({user_id_placeholders})', test_user_ids)
    
    # удаляем тестовых пользователей
    if TEST_EMAILS:
        email_placeholders = ','.join(['%s'] * len(TEST_EMAILS))
        cur.execute(f'DELETE FROM "user" WHERE email IN ({email_placeholders})', TEST_EMAILS)
    
    # удаляем кэш новостей в Redis
    news_keys = redis_client.keys("news*")
    if news_keys:
        redis_client.delete(*news_keys)
    
    redis_client.close()
    conn.commit()
    cur.close()
    conn.close()

# очистка тестовых данных перед и после каждого теста
@pytest.fixture(autouse=True)
def clean_db_before_each_test():
    clean_test_data()
    yield
    clean_test_data()

# создание event loop для асинхронных тестов
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# асинхронный тестовый клиент (возвращаем к старой версии)
@pytest.fixture
async def client():
    async with AsyncClient(base_url=BASE_URL) as client:
        yield client

# данные для тестового пользователя
@pytest.fixture
def test_user_data():
    return {
        "user_name": "Test User",
        "email": "test@example.com",
        "password": "testpass123"
    }

# данные для тестового автора
@pytest.fixture
def test_author_data():
    return {
        "user_name": "Test Author",
        "email": "author@test.com",
        "password": "authorpass123"
    }

# данные мокового администратора из миграций
@pytest.fixture
def mock_admin_data():
    return {
        "email": "polina@mail.ru",
        "password": "12345678"
    }