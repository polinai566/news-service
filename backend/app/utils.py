from argon2 import PasswordHasher

ph = PasswordHasher()

"""Функция для хэширования пароля"""


def hash_password(password: str) -> str:
    return ph.hash(password)
