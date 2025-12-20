from fastapi import Response, Request, status, HTTPException
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from sqlalchemy import select

from app.database import SessionDep, redis_client
from app.user.models import User
from app.user.schemas import UserLogin
from app.utils import check_password, create_jwt, generation_refresh_token
from .schemas import SessionRefreshToken, SessionCreate, SessionAdminRead, SessionRead
from collections.abc import AsyncIterator

import json
import os

load_dotenv()
LIFETIME = int(os.environ["REFRESH_TOKEN_LIFETIME_DAYS"])

class SessionService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание сессии (авторизация)
    async def create(self, payload: UserLogin, response: Response, request: Request) -> SessionCreate | str:

        # получение пользователя из базы данных
        result = await self.db.execute(select(User).where(User.login == payload.login))
        user = result.scalar_one_or_none()
        # проверка существования логина (login)
        if user == None:
            return "This login is not registered"
        # проверка пароля
        if not check_password(payload.password, user.password): 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
        
        # создание JWT токена
        jwt_token = create_jwt(user.user_id, user.user_role) 
        response.headers["x-jwt"] = str(jwt_token)
        # извлечение user_agent из заголовка запроса
        user_agent = request.headers.get("User-Agent")
        # создание refresh токена
        refresh_token = generation_refresh_token()

        new_session = { 
            "user_id": user.user_id,
            "user_agent": user_agent,
            "refresh_token": refresh_token,
            "refresh_token_expiretime": (datetime.now(timezone.utc)+timedelta(days=LIFETIME)).isoformat()
        }

        session_json = json.dumps(new_session)
        lifetime = LIFETIME * 24 * 60 * 60 # в секундах
        try:
            await redis_client.setex(f"session:{user.user_id}:{refresh_token}", lifetime, session_json)
        except Exception as e:
            print(f"Ошибка подключения к Redis: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка подключения к серверу сессий. Убедитесь, что Redis запущен."
            )
        return SessionCreate.model_validate(new_session)
    
    # получение списка сессий конкретного пользователя (для админа или для самого пользователя)
    async def list(self, user_id: int, Schema: SessionAdminRead | SessionRead) -> list[SessionAdminRead] | list[SessionRead]:
        session_keys_iter: AsyncIterator[str] = redis_client.scan_iter(f"session:{user_id}:*") 
        session_keys = [key async for key in session_keys_iter]
        session_list = [
            json.loads(session_data) for key in session_keys
            if (session_data := await redis_client.get(key))
        ]
        sessions = [Schema.model_validate(session) for session in session_list]
        return sessions

    # обновление refresh токена
    async def put(self, payload: SessionRefreshToken, response: Response, request: Request) -> SessionCreate | str:

        user_agent = request.headers.get("User-Agent")
        refresh_token = payload.refresh_token
        session_keys_iter: AsyncIterator[str] = redis_client.scan_iter(f"session:*:{refresh_token}") 
        session_keys = [key async for key in session_keys_iter]
        session_list = [
            json.loads(session_data) for key in session_keys
            if (session_data := await redis_client.get(key))
        ]

        if len(session_list) > 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Violation of referential integrity")
        if len(session_list) == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid")
        key = session_keys[0]
        session = session_list[0]
        if session["user_agent"] != user_agent:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User-Agent is invalid")
        
        expiretime = datetime.fromisoformat(session["refresh_token_expiretime"])
        if datetime.now(timezone.utc) > expiretime:
            await redis_client.delete(key)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The session expired. Log in again")
        
        user = await self.db.execute(select(User).where(User.user_id == session["user_id"]))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token not linked to user")
        
        new_refresh_token = generation_refresh_token()
        jwt_token = create_jwt(session["user_id"], user.user_role)
        response.headers["x-jwt"] = str(jwt_token)
        
        new_session = {
            "user_id": user.user_id,
            "user_agent": user_agent,
            "refresh_token": new_refresh_token,
            "refresh_token_expiretime": (datetime.now(timezone.utc)+timedelta(days=LIFETIME)).isoformat()
        }

        await redis_client.delete(key) # удаление старой сессии

        session_json = json.dumps(new_session)
        lifetime = LIFETIME * 24 * 60 * 60 # в секундах
        await redis_client.setex(f"session:{user.user_id}:{new_refresh_token}", lifetime, session_json)
        return SessionCreate.model_validate(new_session)

    # удаление сессии (выход)
    async def delete(self, request: Request, jwt_payload) -> None | str:
        user_id = jwt_payload['user_id']
        session_keys_iter: AsyncIterator[str] = redis_client.scan_iter(f"session:{user_id}:*")
        session_keys = [key async for key in session_keys_iter]
        session_list = [
            json.loads(session_data) for key in session_keys
            if (session_data := await redis_client.get(key))
        ]
        if session_list == []:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        user_agent = request.headers.get("User-Agent")
        for i in range(len(session_keys)):
            one_session = session_list[i]
            if one_session["user_agent"] == user_agent:
                await redis_client.delete(session_keys[i])
                return "The session was successfully deleted"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your User Agent was not found")