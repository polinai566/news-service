import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_comment_flow(client: TestClient, test_user_dict):
    # регистрация и авторизация пользователя, создание новости
    reg_resp = client.post('/user/register', json=test_user_dict)
    login_resp = client.post('/session/login', json={"username": test_user_dict["username"], "password": test_user_dict["password"]})
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    news_resp = client.post('/news/', json={"title": "news for comment", "content": ""}, headers=headers)
    news_id = news_resp.json().get('id')

    # создание комментария
    comment_data = {"content": "my test comment", "news_id": news_id}
    comm_resp = client.post('/comment/', json=comment_data, headers=headers)
    assert comm_resp.status_code in (200, 201)
    comment_id = comm_resp.json().get('id')

    # чтение комментария
    get_resp = client.get(f'/comment/{comment_id}')
    assert get_resp.status_code == 200
    assert get_resp.json()["content"] == comment_data["content"]

