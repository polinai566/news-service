import pytest

# тест полного цикла работы с комментариями
@pytest.mark.asyncio
async def test_comment_flow(client, test_user_data):
    # регистрация и авторизация пользователя
    await client.post("/user/", json=test_user_data)
    
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = await client.post("/session/", json=login_data)
    paseto_token = login_response.headers["x-paseto"]
    headers = {"Authorization": f"Bearer {paseto_token}"}
    
    # получение списка новостей
    news_response = await client.get("/news/")
    if news_response.status_code == 200:
        news_list = news_response.json()
        if len(news_list) > 0:
            news_id = news_list[0]["news_id"]
            
            # создание комментария
            comment_data = {
                "text": "This is a test comment",
                "news_id": news_id
            }
            comment_response = await client.post("/comment/", json=comment_data, headers=headers)
            assert comment_response.status_code == 200
            comment = comment_response.json()
            assert comment["text"] == comment_data["text"]
            
            # получение комментария для новости
            comments_response = await client.get(f"/comment/news/{news_id}")
            assert comments_response.status_code == 200
            comments = comments_response.json()
            assert len(comments) >= 1
            assert any(c["text"] == comment_data["text"] for c in comments)

    await client.delete("/session/", headers=headers)


# тест создания комментария без авторизации
@pytest.mark.asyncio
async def test_create_comment_unauthorized(client):
    comment_data = {
        "text": "test comment",
        "news_id": 1
    }
    response = await client.post("/comment/", json=comment_data)
    assert response.status_code == 401


# тест получения комментариев для несуществующей новости
@pytest.mark.asyncio
async def test_get_comments_for_nonexistent_news(client):
    response = await client.get("/comment/news/99999")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)
    assert len(comments) == 0


# тест создания комментария к несуществующей новости
@pytest.mark.asyncio
async def test_create_comment_for_nonexistent_news(client, test_user_data):
    # регистрация и авторизация
    await client.post("/user/", json=test_user_data)
    
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = await client.post("/session/", json=login_data)
    paseto_token = login_response.headers["x-paseto"]
    headers = {"x-paseto": paseto_token}
    
    # попытка создать комментарий к несуществующей новости
    comment_data = {
        "text": "comment to nonexistent news",
        "news_id": 99999
    }
    response = await client.post("/comment/", json=comment_data, headers=headers)
    assert response.status_code != 200

    await client.delete("/session/", headers=headers)


# тест получения конкретного комментария
@pytest.mark.asyncio
async def test_get_single_comment(client):
    # сначала получаем список новостей
    news_response = await client.get("/news/")
    if news_response.status_code == 200:
        news_list = news_response.json()
        if len(news_list) > 0:
            news_id = news_list[0]["news_id"]
            
            # получение комментария для этой новости
            comments_response = await client.get(f"/comment/news/{news_id}")
            if comments_response.status_code == 200:
                comments = comments_response.json()
                if len(comments) > 0:
                    comment_id = comments[0]["comment_id"]
                    
                    # получение конкретного комментария по ID
                    comment_response = await client.get(f"/comment/{comment_id}")
                    assert comment_response.status_code == 200
                    comment = comment_response.json()
                    assert comment["comment_id"] == comment_id
                    assert "text" in comment