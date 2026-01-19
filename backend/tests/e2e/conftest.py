import pytest
from playwright.sync_api import sync_playwright

# фикстура для браузера
@pytest.fixture(scope="session")
def browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,  # Для отладки False, для CI/CD можно True
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    yield browser
    browser.close()
    playwright.stop()

# фикстура для контекста браузера
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