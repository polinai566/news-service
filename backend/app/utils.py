from argon2 import PasswordHasher
from jwt import InvalidSignatureError, ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import jwt
import random
import string
import os

ph = PasswordHasher()

"""Функция для хэширования пароля"""

def hash_password(password: str) -> str:
    return ph.hash(password)

'''Функция для проверки пароля'''
def check_password(password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, password)
        return True
    except Exception:
        return False

load_dotenv()
SECRET_KEY = os.environ["JWT_SECRET_KEY"]
LIFETIME = int(os.environ["JWT_LIFETIME_MINUTES"])

'''Функция создания JWT-токена'''
def create_jwt(user_id: int, user_role: str, secret_key: str = SECRET_KEY, lifetime: int = LIFETIME):
    jwt_token = jwt.encode({"user_id": str(user_id),
                                "user_role": user_role,
                                "exp": datetime.now(timezone.utc) + timedelta(minutes=lifetime)}, 
                                secret_key, algorithm="HS256")
    return jwt_token

'''Функция проверки корректности JWT-токена'''
def check_jwt(jwt_token: str, secret_key: str = SECRET_KEY):
    try:
        payload = jwt.decode(jwt_token, secret_key, algorithms="HS256", options={"verify_exp": True})
        return payload
    except InvalidSignatureError:
        return False
    except ExpiredSignatureError:
        return False
    except InvalidTokenError:
        return False
    
'''Функция генерации refresh-токена'''
def generation_refresh_token() -> str:
    characters = string.ascii_letters + string.digits
    refresh_token = ''.join(random.choices(characters, k=32))
    return refresh_token