from typing import Sequence
from sqlalchemy import select

from app.database import SessionDep
from .models import User
from .schemas import UserCreate, UserUpdate
from app.utils import check_jwt, hash_password

class UserService:
    def __init__(self, db: SessionDep):
        self.db = db

    # регистрация пользователя
    async def create(self, payload: UserCreate) -> User | str:
        # проверка уникальности email
        existing_user = await self.db.execute(select(User).where(User.email == payload.email))
        if existing_user.scalar_one_or_none():
            return "Email already registered"
        payload.password = hash_password(payload.password)
        new_user = User(**payload.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    # чтение списка пользователей
    async def list(self, jwt_token: str) -> Sequence[User] | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        if jwt_payload["user_role"] == "admin":
            users = await self.db.execute(select(User))
            return users.scalars().all()
        else:
            return "Permission denied"

    # чтение пользователя по индексу
    async def get(self, user_id: int, jwt_token: str) -> User | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        if jwt_payload["user_role"] == "admin" or jwt_payload["user_id"] == user_id:
            user = await self.db.execute(select(User).where(User.user_id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                return "User not found"
            return user
        else:
            return "Permission denied"

    # обновление пользователя
    async def update(self, user_id: int, payload: UserUpdate, jwt_token: str) -> User | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        if jwt_payload["user_role"] == "admin" or jwt_payload["user_id"] == user_id:
            user = await self.db.execute(select(User).where(User.user_id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                return "User not found"
            user.password = hash_password(user.password) 
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        else:
            return "Permission denied"

    # удаление пользователя
    async def delete(self, user_id: int, jwt_token: str) -> None | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        if jwt_payload["user_role"] == "admin" or jwt_payload["user_id"] == user_id:
            user = await self.db.execute(select(User).where(User.user_id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                return "User not found"
            await self.db.delete(user)
            await self.db.commit()
            return "The user was successfully deleted"
        else:
            return "Permission denied"