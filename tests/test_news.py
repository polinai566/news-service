import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_news_crud_flow(client: TestClient, test_user_dict):
    # регистрация пользователя
    resp = client.post('/user/register', json=test_user_dict)
    assert resp.status_code in (200, 201), resp.text
    user = resp.json()

    # авторизация
    login_data = {"username": test_user_dict['username'], "password": test_user_dict['password']}
    login_resp = client.post('/session/login', json=login_data)
    assert login_resp.status_code in (200, 201), login_resp.text
    token = login_resp.json().get("access_token")

    # создание новости
    news_data = {"title": "Test News", "content": "Test content"}
    headers = {"Authorization": f"Bearer {token}"}
    news_resp = client.post('/news/', json=news_data, headers=headers)
    assert news_resp.status_code in (200, 201), news_resp.text
    news_id = news_resp.json().get('id')

    # чтение новости
    read_resp = client.get(f'/news/{news_id}')
    assert read_resp.status_code == 200, read_resp.text
    assert read_resp.json()['title'] == news_data['title']

    # редактирование новости
    new_data = {"title": "Updated News", "content": "Updated content"}
    upd_resp = client.put(f'/news/{news_id}', json=new_data, headers=headers)
    assert upd_resp.status_code == 200
    assert upd_resp.json()['title'] == new_data['title']

    # удаление новости
    del_resp = client.delete(f'/news/{news_id}', headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()['ok'] is True

