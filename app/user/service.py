from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import select

from app.database import SessionDep
from .models import User
from .schemas import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание пользователя
    async def create(self, payload: UserCreate) -> User:
        # проверка уникальности email
        existing_user = await self.db.execute(select(User).where(User.email == payload.email))
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(**payload.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    # чтение списка пользователей
    async def list(self) -> Sequence[User]:
        users = await self.db.execute(select(User))
        return users.scalars().all()

    # чтение пользователя по индексу
    async def get(self, user_id: int) -> User:
        user = await self.db.execute(select(User).where(User.user_id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    # обновление пользователя
    async def update(self, user_id: int, payload: UserUpdate) -> User:
        user = await self.db.execute(select(User).where(User.user_id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    # удаление пользователя
    async def delete(self, user_id: int) -> None:
        user = await self.db.execute(select(User).where(User.user_id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await self.db.delete(user)
        await self.db.commit()