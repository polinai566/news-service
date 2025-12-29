import pytest
from playwright.sync_api import sync_playwright
from datetime import datetime

FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

# фикстура для браузера (синхронная)
@pytest.fixture(scope="session")
def browser():
    playwright = sync_playwright().start()
    
    browser = playwright.chromium.launch(
        headless=False,  # Сначала сделайте False для отладки
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    
    yield browser
    browser.close()
    playwright.stop()

# Фикстура для контекста браузера
@pytest.fixture
def context(browser):
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        ignore_https_errors=True
    )
    
    yield context
    context.close()

# фикстура для страницы
@pytest.fixture
def page(context):
    page = context.new_page()
    page.set_default_timeout(30000)
    yield page
    
# тестовый пользователь для e2e тестов
@pytest.fixture
def test_user():
    return {
        "username": "e2e_test_user",
        "email": "e2e_test@example.com",
        "password": "TestPassword123!",
        "role": "user"
    }

# тестовый автор из миграций
@pytest.fixture
def test_author():
    return {
        "email": "mitya@mail.ru",
        "password": "87654321",
        "name": "Mitya"
    }

# тестовый администратор из миграций
@pytest.fixture
def test_admin():
    return {
        "email": "polina@mail.ru",
        "password": "12345678",
        "name": "Polina"
    }

@pytest.fixture
def test_news():
    """Тестовая новость для e2e тестов"""
    return {
        "title": "E2E Test News - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": """Это тестовая новость, она была создана автоматически.

Первый абзац текста.

Второй абзац текста.

А это конец новости!""",
        "cover": "https://images.unsplash.com/photo-1586769852836-bc069f19e1b6?w=800&auto=format&fit=crop"
    }

