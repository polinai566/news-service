from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy import select

from app.database import SessionDep, redis_client
from .models import User
from .schemas import UserCreate, UserUpdate
from app.utils import hash_password

class UserService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание пользователя
    async def create(self, payload: UserCreate) -> User | str:
        # проверка уникальности login
        existing_user = await self.db.execute(select(User).where(User.login == payload.login))
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already registered")
        payload.password = hash_password(payload.password)
        new_user = User(**payload.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    # чтение списка пользователей
    async def list(self) -> Sequence[User]:
        users = await self.db.execute(select(User))
        users_list = users.scalars().all()
        if not users_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
        return users_list

    # чтение пользователя по индексу
    async def get(self, user_id: int) -> User:
        user = await self.db.execute(select(User).where(User.user_id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    # обновление пользователя
    async def update(self, user_id: int, payload: UserUpdate) -> User:
        user = await self.db.execute(select(User).where(User.user_id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        update_data = payload.model_dump(exclude_unset=True)
        if 'login' in update_data and update_data['login'] != user.login:
            existing_user = await self.db.execute(
                select(User).where(User.login == update_data['login'])
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already registered")
        if 'password' in update_data and update_data['password']:
            update_data['password'] = hash_password(update_data['password'])
        elif 'password' in update_data:
            del update_data['password']
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        # при обновлении данных о пользователе удаляем все его активные сессии, если были
        session_keys_iter = redis_client.scan_iter(f"session:{user.user_id}:*")
        session_keys = [key async for key in session_keys_iter]
        if session_keys != []:
            for key in session_keys: await redis_client.delete(key)
        return user

    # удаление пользователя
    async def delete(self, user_id: int) -> str:
        user = await self.db.execute(select(User).where(User.user_id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.db.delete(user)
        await self.db.commit()
        # при удалении пользователя удаляем все его активные сессии, если были
        session_keys_iter = redis_client.scan_iter(f"session:{user.user_id}:*")
        session_keys = [key async for key in session_keys_iter]
        if session_keys != []:
            for key in session_keys: await redis_client.delete(key)
        return "The user was successfully deleted"