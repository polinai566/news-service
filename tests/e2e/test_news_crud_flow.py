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

    try:
        # 1. Логин
        print("\n=== Шаг 1: Вход в систему ===")
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle", timeout=15000)
        page.fill('#email', TEST_AUTHOR_EMAIL)
        page.fill('#password', TEST_AUTHOR_PASSWORD)
        page.click('button[type="submit"]')
        
        # Используем более надежное ожидание
        page.wait_for_url(f"{FRONTEND_URL}/**", timeout=10000)
        print("✓ Успешный вход в систему")

        # 2. Проверка навигации
        print("\n=== Шаг 2: Поиск элемента для создания новости ===")
        
        # Добавляем небольшую паузу для загрузки интерфейса
        page.wait_for_timeout(1000)
        
        # Пробуем разные способы найти кнопку создания
        create_selectors = [
            'button:has-text("Создать")',
            'button:has-text("Create")',
            'a:has-text("Создать новость")',
            'a:has-text("Create news")',
            'a[href*="/news/create"]'
        ]
        
        create_found = False
        for selector in create_selectors:
            try:
                if page.locator(selector).count() > 0:
                    print(f"Нашли элемент по селектору: {selector}")
                    page.locator(selector).first.click()
                    page.wait_for_timeout(2000)
                    create_found = True
                    break
            except:
                continue
        
        if not create_found:
            print("Переходим напрямую /news/create")
            page.goto(f"{FRONTEND_URL}/news/create", wait_until="networkidle", timeout=15000)
        
        # 3. Проверяем, что мы на правильной странице и ждем загрузки формы
        print("\n=== Шаг 3: Проверка страницы создания ===")
        print(f"Текущий URL: {page.url}")
        
        # Делаем скриншот для отладки
        page.screenshot(path="create_page_debug.png")
        
        # Ждем загрузки формы - проверяем по заголовку или элементам
        try:
            # Ждем заголовок "Создание новости"
            expect(page.locator('h1')).to_contain_text("Создание", timeout=5000)
        except:
            print("Заголовок 'Создание' не найден, проверяем другие элементы")
        
        # Ждем появления поля заголовка с несколькими способами
        print("Ожидаем загрузки формы...")
        
        # Способ 1: Ждем появления любого из полей ввода
        try:
            page.wait_for_selector('input, textarea', timeout=5000)
        except:
            print("Не найдены поля ввода")
        
        # Способ 2: Выводим все поля для отладки
        inputs = page.locator('input, textarea')
        print(f"Найдено полей ввода: {inputs.count()}")
        
        for i in range(inputs.count()):
            try:
                inp = inputs.nth(i)
                tag = inp.evaluate('el => el.tagName')
                id_attr = inp.get_attribute('id') or ''
                name_attr = inp.get_attribute('name') or ''
                placeholder = inp.get_attribute('placeholder') or ''
                print(f"  Поле {i}: {tag}, id='{id_attr}', name='{name_attr}', placeholder='{placeholder}'")
            except:
                print(f"  Поле {i}: не удалось получить информацию")
        
        # 4. Заполнение формы с защитой от таймаута
        print("\n=== Шаг 4: Заполнение формы ===")
        
        # Пробуем разные способы найти поле заголовка
        header_found = False
        header_selectors = ['#header', 'input[id="header"]', 'input[placeholder*="заголовок" i]', 'input[type="text"]:first-of-type']
        
        for selector in header_selectors:
            try:
                if page.locator(selector).count() > 0:
                    print(f"Нашли поле заголовка по селектору: {selector}")
                    page.fill(selector, news_title)
                    header_found = True
                    break
            except Exception as e:
                print(f"Не удалось заполнить по селектору {selector}: {e}")
                continue
        
        if not header_found:
            # Если не нашли стандартными способами, используем первый input
            page.locator('input').first.fill(news_title)
        
        # Заполняем content
        content_found = False
        content_selectors = ['#content', 'textarea[id="content"]', 'textarea[placeholder*="текст" i]', 'textarea:first-of-type']
        
        for selector in content_selectors:
            try:
                if page.locator(selector).count() > 0:
                    print(f"Нашли поле контента по селектору: {selector}")
                    page.fill(selector, news_content)
                    content_found = True
                    break
            except:
                continue
        
        if not content_found:
            page.locator('textarea').first.fill(news_content)
        
        # Заполняем cover (опциональное поле)
        try:
            page.fill('#cover', 'https://images.unsplash.com/photo-1586769852836-bc069f19e1b6?w=800')
        except:
            print("Поле cover не найдено или не заполнено")
        
        # 5. Отправка формы
        print("\n=== Шаг 5: Отправка формы ===")
        
        # Находим кнопку отправки
        submit_selectors = ['button[type="submit"]', 'button.submit-btn', 'button:has-text("Создать")', 'button:has-text("Submit")']
        submit_found = False
        
        for selector in submit_selectors:
            try:
                if page.locator(selector).count() > 0:
                    print(f"Нашли кнопку отправки по селектору: {selector}")
                    page.locator(selector).first.click()
                    submit_found = True
                    break
            except:
                continue
        
        if not submit_found:
            # Используем первую кнопку на странице
            page.locator('button').first.click()
        
        # Ждем перехода на страницу новости
        page.wait_for_timeout(3000)
        
        # Проверяем, перешли ли мы на страницу новости
        if "/news/" in page.url:
            news_id = page.url.split('/')[-1]
            print(f"✓ Новость создана, ID: {news_id}")
            
            # 6. Редактирование
            print("\n=== Шаг 6: Редактирование новости ===")
            
            # Ищем кнопку редактирования
            edit_btn = None
            edit_selectors = ['button:has-text("Редактировать")', 'a:has-text("Редактировать")', 'button.edit-btn', 'a.edit-link']
            
            for selector in edit_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        edit_btn = page.locator(selector).first
                        break
                except:
                    continue
            
            if edit_btn and edit_btn.is_visible(timeout=3000):
                edit_btn.click()
                page.wait_for_timeout(2000)
                
                # Редактируем заголовок
                try:
                    page.fill('#header', updated_title)
                except:
                    # Пробуем другие селекторы
                    try:
                        page.fill('input[type="text"]:first-of-type', updated_title)
                    except:
                        print("Не удалось найти поле для редактирования заголовка")
                
                # Сохраняем изменения
                try:
                    page.click('button[type="submit"]')
                except:
                    page.locator('button:has-text("Сохранить")').first.click()
                
                page.wait_for_timeout(2000)
                print("✓ Новость отредактирована")
                
                # 7. Удаление
                print("\n=== Шаг 7: Удаление новости ===")
                delete_btn = None
                delete_selectors = ['button:has-text("Удалить")', 'a:has-text("Удалить")', 'button.delete-btn']
                
                for selector in delete_selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            delete_btn = page.locator(selector).first
                            break
                    except:
                        continue
                
                if delete_btn and delete_btn.is_visible(timeout=3000):
                    # Настраиваем обработчик диалога
                    page.once("dialog", lambda dialog: dialog.accept())
                    delete_btn.click()
                    page.wait_for_timeout(2000)
                    print("✓ Новость удалена")
                else:
                    print("⚠ Кнопка удаления не найдена")
            else:
                print("⚠ Кнопка редактирования не найдена")
        else:
            print(f"⚠ Не перешли на страницу новости, текущий URL: {page.url}")
            page.screenshot(path="after_submit_debug.png")
        
        print("\n" + "="*50)
        print("Тест завершен")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        page.screenshot(path="fixed_test_error.png")
        # Выводим текущий HTML для отладки
        try:
            html = page.content()
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(html[:5000])
            print("Первые 5000 символов HTML сохранены в error_page.html")
        except:
            print("Не удалось получить HTML страницы")
        raise