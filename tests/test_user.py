import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_user_register_and_login(client: TestClient, test_user_dict):
    resp = client.post('/user/register', json=test_user_dict)
    assert resp.status_code in (200, 201), resp.text
    login_data = {"username": test_user_dict['username'], "password": test_user_dict['password']}
    login_resp = client.post('/session/login', json=login_data)
    assert login_resp.status_code in (200, 201), login_resp.text
    assert 'access_token' in login_resp.json()

