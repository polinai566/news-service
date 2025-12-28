import pytest

# получение списка новостей
@pytest.mark.asyncio
async def test_get_empty_news_list(client):
    response = await client.get("/news/")
    # если нет новостей, то должно быть 404
    if response.status_code == 404:
        assert "No news found" in response.json()["detail"]
    else:
        # если есть какие-то данные
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# создание новости без авторизации
@pytest.mark.asyncio
async def test_create_news_unauthorized(client):
    news_data = {
        "header": "Test News",
        "content": "Test content",
        "cover": "https://example.com/image.jpg"
    }
    response = await client.post("/news/", json=news_data)
    assert response.status_code == 401


# создание пользователя, обновление роли и создание новости
@pytest.mark.asyncio
async def test_full_news_flow(client, test_user_data, mock_admin_data):
    # создаем нового пользователя (по умолчанию role='user')
    user_response = await client.post("/user/", json=test_user_data)
    assert user_response.status_code == 200
    user_id = user_response.json()["user_id"]
    
    # авторизация админа
    admin_login_response = await client.post("/session/", json=mock_admin_data)
    assert admin_login_response.status_code == 200
    admin_jwt = admin_login_response.headers.get("x-jwt")
    admin_headers = {"Authorization": f"Bearer {admin_jwt}"}

    # обновление роли нового пользователя
    update_data = {
        "user_name": test_user_data["user_name"],
        "email": test_user_data["email"],
        "user_role": "author"  # смена роли с user на author
    }
    
    update_response = await client.put(f"/user/{user_id}", json=update_data, headers=admin_headers)
    assert update_response.status_code == 200

    updated_user = update_response.json()
    assert updated_user["user_role"] == "author"
    await client.delete("/session/", headers=admin_headers)

    # авторизация автора
    user_login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    user_login_response = await client.post("/session/", json=user_login_data)
    assert user_login_response.status_code == 200
    user_jwt = user_login_response.headers.get("x-jwt")
    user_headers = {"Authorization": f"Bearer {user_jwt}"}

    # создание новости автором
    news_data = {
        "header": "My First News",
        "content": "This is a test news article",
        "cover": "https://example.com/image.jpg"
    }
    news_response = await client.post("/news/", json=news_data, headers=user_headers)
    assert news_response.status_code == 200
    
    news = news_response.json()
    assert news["header"] == news_data["header"]
    news_id = news["news_id"]
    
    # получение списка всех новостей
    list_response = await client.get("/news/")
    assert list_response.status_code == 200
    news_list = list_response.json()
    assert isinstance(news_list, list)
    
    # получение конкретной новости по ID
    single_response = await client.get(f"/news/{news_id}")
    assert single_response.status_code == 200
    single_news = single_response.json()
    assert single_news["news_id"] == news_id
    assert single_news["header"] == news_data["header"]

    await client.delete("/session/", headers=user_headers)