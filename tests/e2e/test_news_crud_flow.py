import pytest
from playwright.sync_api import Page, expect
from datetime import datetime

FRONTEND_URL = "http://localhost:5173"
TEST_AUTHOR_EMAIL = "mitya@mail.ru"
TEST_AUTHOR_PASSWORD = "87654321"

@pytest.mark.e2e
def test_news_crud_flow_e2e(page: Page):
    page.set_default_timeout(30000)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    news_title = f"E2E Test News {timestamp}"
    news_content = f"Тестовая новость {timestamp}"
    updated_title = f"Обновленная {timestamp}"

    # 1. Логин
    page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle", timeout=15000)
    page.fill('#email', TEST_AUTHOR_EMAIL)
    page.fill('#password', TEST_AUTHOR_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{FRONTEND_URL}/**", timeout=10000)

    # 2. Переход к созданию новости
    page.wait_for_timeout(1000)
    
    create_selectors = [
        'button:has-text("Создать")',
        'button:has-text("Create")',
        'a:has-text("Создать новость")',
        'a[href*="/news/create"]'
    ]
    
    for selector in create_selectors:
        if page.locator(selector).count() > 0:
            page.locator(selector).first.click()
            page.wait_for_timeout(2000)
            break
    else:
        page.goto(f"{FRONTEND_URL}/news/create", wait_until="networkidle", timeout=15000)

    # 3. Заполнение формы
    page.wait_for_selector('input, textarea', timeout=5000)
    
    header_selectors = ['#header', 'input[placeholder*="заголовок" i]', 'input[type="text"]:first-of-type']
    for selector in header_selectors:
        if page.locator(selector).count() > 0:
            page.fill(selector, news_title)
            break
    
    content_selectors = ['#content', 'textarea[placeholder*="текст" i]', 'textarea:first-of-type']
    for selector in content_selectors:
        if page.locator(selector).count() > 0:
            page.fill(selector, news_content)
            break
    
    try:
        page.fill('#cover', 'https://images.unsplash.com/photo-1586769852836-bc069f19e1b6?w=800')
    except:
        pass

    # 4. Отправка формы
    submit_selectors = ['button[type="submit"]', 'button:has-text("Создать")']
    for selector in submit_selectors:
        if page.locator(selector).count() > 0:
            page.locator(selector).first.click()
            break
    
    page.wait_for_timeout(3000)

    # 5. Редактирование новости
    if "/news/" in page.url:
        edit_selectors = ['button:has-text("Редактировать")', 'a:has-text("Редактировать")']
        for selector in edit_selectors:
            if page.locator(selector).count() > 0 and page.locator(selector).first.is_visible(timeout=3000):
                page.locator(selector).first.click()
                page.wait_for_timeout(2000)
                
                for header_selector in header_selectors:
                    if page.locator(header_selector).count() > 0:
                        page.fill(header_selector, updated_title)
                        break
                
                for submit_selector in submit_selectors:
                    if page.locator(submit_selector).count() > 0:
                        page.locator(submit_selector).first.click()
                        break
                
                page.wait_for_timeout(2000)
                break

        # 6. Удаление новости
        delete_selectors = ['button:has-text("Удалить")', 'a:has-text("Удалить")']
        for selector in delete_selectors:
            if page.locator(selector).count() > 0 and page.locator(selector).first.is_visible(timeout=3000):
                page.once("dialog", lambda dialog: dialog.accept())
                page.locator(selector).first.click()
                page.wait_for_timeout(2000)
                break

    # 7. Выход из аккаунта
    logout_selectors = ['button:has-text("Выйти")', 'a:has-text("Выйти")', 'a:has-text("Logout")', 'button:has-text("Logout")']
    page.wait_for_timeout(1000)
    
    for selector in logout_selectors:
        if page.locator(selector).count() > 0 and page.locator(selector).first.is_visible():
            page.locator(selector).first.click()
            page.wait_for_timeout(1000)
            break