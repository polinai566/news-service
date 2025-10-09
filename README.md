# Новостной сервис

## Описание сервиса

При помощи сервиса можно создавать, изменять, удалять и извлекать сущности: User, News, Comment.

## Визуализация моделей сущностей и их связей

![ER-диаграмма](resources/ER-диаграмма.png)

## Шаги для запуска сервиса

1. В файлах app/database.py и alembic.ini изменить параметры для подключения к вашей базе данных в строках:

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/webdev" (app/database.py, 6 строка)
sqlalchemy.url = postgresql://postgres:password@localhost:5432/webdev (alembic.ini, 86 строка)

2. Создать и активировать вирутальное окружение:

python -m venv .venv
.venv\Scripts\Activate.ps1

3. Установить необходимые зависимости:

pip install fastapi
pip install uvicorn
pip install sqlalchemy[asyncio] asyncpg
pip install alembic
pip install pydantic[email]
pip install psycopg2-binary

4. Применить миграции

alembic upgrade head

Для отката последней миграции используйте команду:
alembic downgrade -1

5. Запустить приложение

uvicorn app.main:app

## Описание и использование ручек

Описание каждого из методов CRUD для каждой сущности можно посмотреть с помощью инструмента Swagger после запуска приложения по адресу http://127.0.0.1:8000/docs. Там же можно протестировать работу приложения.

## Описание миграций

Миграция "Initial tables" была создана при помощи команды:
alembic revision --autogenerate -m "Initial tables"
Она инициализирует таблицы.

Миграция "Add users, news and comment" была создана при помощи команды:
alembic revision -m "Add users, news and comment"
Она может создавать и удалять пользователей, новость, написанную одним из пользователем, и комментарий, написанный другим пользователем.