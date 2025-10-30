from fastapi import Response, Request
from typing import Sequence
from sqlalchemy import select
from datetime import datetime

from app.database import SessionDep
from app.user.models import User
from app.user.schemas import UserLogin
from .schemas import SessionRefreshToken
from app.utils import check_password, create_jwt, generation_refresh_token, check_jwt, get_privileges
from .models import Session
# from .schemas import SessionRead

class SessionService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание сессии (авторизация)
    async def create(self, payload: UserLogin, response: Response, request: Request) -> Session | str:

        # получение пользователя из базы данных
        result = await self.db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        # проверка существования логина (email)
        if user == None:
            return "This email is not registered"
        # проверка пароля
        if not check_password(payload.password, user.password): # type: ignore
            return "Incorrect password"
        # создание JWT токена
        jwt_token = create_jwt(user.user_id, user.user_role) # type: ignore
        response.headers["X-JWT"] = str(jwt_token)
        # извлечение user_agent из заголовка запроса
        user_agent = request.headers.get("User-Agent")
        # создание refresh токена
        refresh_token = generation_refresh_token()
        # создание новой сессии и добавление её в базу данных
        new_session = Session(
            refresh_token=refresh_token,
            user_id=user.user_id,
            user_agent=user_agent
        )
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        return new_session
    
    # получение списка сессий
    async def list(self, jwt_token: str) -> Sequence[Session] | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        if jwt_payload["user_role"] == "admin":
            news = await self.db.execute(select(Session))
            return news.scalars().all()
        else:
            return "Permission denied"
    
    # получение сессии по индексу
    async def get(self, session_id: int, jwt_token: str) -> Session | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        session = await self.db.execute(select(Session).where(Session.session_id == session_id))
        session = session.scalar_one_or_none()
        if not session:
            return "Session not found"
        if jwt_payload["user_role"] == "admin" or jwt_payload["user_id"] == session.user_id: # type: ignore
            return session
        else:
            return "Permission denied"

    # обновление refresh токена
    async def put(self, payload: SessionRefreshToken, jwt_token: str, response: Response, request: Request) -> Session | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        user_agent = request.headers.get("User-Agent")
        session = await self.db.execute(select(Session).where(Session.refresh_token == payload.refresh_token and Session.user_agent == user_agent))
        session = session.scalar_one_or_none()
        if not session:
            return "User-Agent or Refresh token is invalid"
        if session.refresh_token_lifetime > datetime.now(): # type: ignore
            await self.db.delete(session)
            await self.db.commit()
            return "The session expired. Log in again"
        refresh_token = generation_refresh_token()
        jwt_token = create_jwt(jwt_payload["user_id"], jwt_payload["user_role"])
        response.headers["X-JWT"] = str(jwt_token)
        new_session = Session(
            refresh_token=refresh_token,
            user_id=jwt_payload["user_id"],
            user_agent=user_agent
        )
        await self.db.delete(session)
        await self.db.commit()
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        return new_session

    # удаление сессии (выход)
    async def delete(self, session_id: int, jwt_token: str) -> None | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        session = await self.db.execute(select(Session).where(Session.session_id == session_id))
        session = session.scalar_one_or_none()
        if not session:
            return "Session not found"
        rights = get_privileges(jwt_payload, session.user_id) # type: ignore
        if rights in ["admin", "author_same", "user_same"]:
            await self.db.delete(session)
            await self.db.commit()
            return "The session was successfully deleted"
        return "Permission denied"