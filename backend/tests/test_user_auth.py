import pytest

# успешная регистрация пользователя
@pytest.mark.asyncio
async def test_successful_registration(client, test_user_data):
    response = await client.post("/user/", json=test_user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["user_name"] == test_user_data["user_name"]
    assert "user_id" in data
    assert "user_role" in data
    assert data["user_role"] == "user"  # роль user по умолчанию


# регистрация с уже существующим email
@pytest.mark.asyncio
async def test_duplicate_email_registration(client, test_user_data):
    # первая регистрация
    resp1 = await client.post("/user/", json=test_user_data)
    assert resp1.status_code == 200
    
    # вторая попытка с тем же email
    resp2 = await client.post("/user/", json=test_user_data)
    assert resp2.status_code == 409
    assert "Email already registered" in resp2.json()["detail"]


# успешная авторизация
@pytest.mark.asyncio
async def test_successful_login(client, test_user_data):
    # сначала регистрация
    await client.post("/user/", json=test_user_data)
    
    # потом авторизация
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = await client.post("/session/", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "refresh_token" in data
    assert "x-paseto" in response.headers  # PASETO в заголовках
    
    # logout после теста
    paseto_token = response.headers["x-paseto"]
    headers = {"Authorization": f"Bearer {paseto_token}"}
    logout_response = await client.delete("/session/", headers=headers)
    assert logout_response.status_code == 200


# авторизация с неправильным паролем
@pytest.mark.asyncio
async def test_wrong_password_login(client, test_user_data):
    # регистрация
    await client.post("/user/", json=test_user_data)
    
    # логин с неправильным паролем
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword"
    }
    response = await client.post("/session/", json=login_data)
    
    assert response.status_code == 401
    assert "Incorrect password" in response.json()["detail"]


# авторизация с несуществующим email
@pytest.mark.asyncio
async def test_nonexistent_email_login(client):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    response = await client.post("/session/", json=login_data)
    
    # "This email is not registered"
    assert response.status_code == 404
    assert "This email is not registered" in response.text