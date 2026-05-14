from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi_sso.sso.github import GithubSSO
from argon2 import PasswordHasher
from pyseto import Key
import pyseto
import random
import string
import json
import os
import httpx
import hashlib

load_dotenv()

SECRET_KEY = os.environ["PASETO_SECRET_KEY"]
LIFETIME = int(os.environ["PASETO_LIFETIME_MINUTES"])

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]
GITHUB_CLIENT_REDIRECT = os.environ["GITHUB_CLIENT_REDIRECT"]

timeout = httpx.Timeout(30.0)
sso = GithubSSO(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    redirect_uri=GITHUB_CLIENT_REDIRECT,
    allow_insecure_http=True,
)
    
'''Функция генерации 32-битного ключа для PASETO на основе ключа из переменной окружения PASETO_SECRET_KEY'''
def get_paseto_key() -> Key:
    secret_str = SECRET_KEY
    key_bytes = hashlib.sha256(secret_str.encode()).digest()
    return Key.new(version=4, purpose="local", key=key_bytes)

'''Функция создания PASETO v4.local (шифрование)'''
def create_paseto_token(user_id: int, user_role: str, lifetime: int = LIFETIME) -> str:
    now = datetime.now(timezone.utc) # время сейчас
    exp = now + timedelta(minutes=lifetime) # время, когда истечёт PASETO
    payload = {
        "user_id": user_id,
        "user_role": user_role,
        "exp": int(exp.timestamp()),
    }
    key = get_paseto_key()
    token = pyseto.encode(key, payload) # генерация с ключом и полезной нагрузкой
    return token.decode("utf-8")

'''Функция проверки PASETO токена'''
def check_paseto_token(token: str) -> dict | bool:
    try:
        key = get_paseto_key()
        decoded = pyseto.decode(key, token)
        payload_bytes = decoded.payload
        payload = json.loads(payload_bytes.decode('utf-8'))
        # проверка срока действия
        exp = payload.get("exp")
        if exp and isinstance(exp, (int, float)):
            if datetime.now(timezone.utc).timestamp() > exp:
                return False
        return payload
    except Exception:
        return False
    
'''Функция генерации refresh-токена'''
def generation_refresh_token() -> str:
    characters = string.ascii_letters + string.digits
    refresh_token = ''.join(random.choices(characters, k=32))
    return refresh_token

ph = PasswordHasher()

'''Функция для хэширования пароля'''
def hash_password(password: str) -> str:
    return ph.hash(password)

'''Функция для проверки пароля'''
def check_password(password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, password)
        return True
    except Exception:
        return False