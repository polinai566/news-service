from fastapi import Response, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from collections.abc import AsyncIterator
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from app.database import SessionDep, redis_client
from app.utils import check_password, create_jwt, generation_refresh_token, check_jwt, sso
from app.user.models import User
from app.user.schemas import UserLogin
from .schemas import SessionRefreshToken, SessionCreate, SessionAdminRead, SessionRead

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
        result = await self.db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        # проверка существования логина (email)
        if user == None:
            return "This email is not registered"
        # проверка пароля
        if not check_password(payload.password, user.password): 
            return "Incorrect password"
        
        # создание JWT токена
        jwt_token = create_jwt(user.user_id, user.user_role) 
        response.headers["X-JWT"] = str(jwt_token)
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
        await redis_client.setex(f"session:{user.user_id}:{refresh_token}", lifetime, session_json)
        return SessionCreate.model_validate(new_session)
    
    # получение списка сессий конкретного пользователя (для админа и для самого пользователя)
    async def list(self, user_id: int, jwt_token: str) -> list[SessionAdminRead] | list[SessionRead] | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        session_keys_iter: AsyncIterator[str] = redis_client.scan_iter(f"session:{user_id}:*") 
        session_keys = [key async for key in session_keys_iter]
        session_list = [
            json.loads(session_data) for key in session_keys
            if (session_data := await redis_client.get(key))
        ]
        if jwt_payload["user_role"] == "admin":
            admin_sessions: list[SessionAdminRead] = [SessionAdminRead.model_validate(session) for session in session_list]
            return admin_sessions
        if jwt_payload["user_id"] == user_id:
            user_sessions: list[SessionRead] = [SessionRead.model_validate(session) for session in session_list]
            return user_sessions
        else:
            return "Permission denied"

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
            return "Violation of referential integrity"
        if len(session_list) == 0:
            return "Refresh token is invalid"
        key = session_keys[0]
        session = session_list[0]
        if session["user_agent"] != user_agent:
            "User-Agent is invalid"
        
        expiretime = datetime.fromisoformat(session["refresh_token_expiretime"])
        if datetime.now(timezone.utc) > expiretime:
            await redis_client.delete(key)
            return "The session expired. Log in again"
        
        user = await self.db.execute(select(User).where(User.user_id == session["user_id"]))
        user = user.scalar_one_or_none()
        if not user:
            return "Refresh token not linked to user"
        
        new_refresh_token = generation_refresh_token()
        jwt_token = create_jwt(session["user_id"], user.user_role)
        response.headers["X-JWT"] = str(jwt_token)
        
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
    async def delete(self, request: Request, jwt_token: str) -> None | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        user_id = jwt_payload['user_id']
        session_keys_iter: AsyncIterator[str] = redis_client.scan_iter(f"session:{user_id}:*")
        session_keys = [key async for key in session_keys_iter]
        session_list = [
            json.loads(session_data) for key in session_keys
            if (session_data := await redis_client.get(key))
        ]
        if session_list == []:
            return "Session not found"
        user_agent = request.headers.get("User-Agent")
        for i in range(len(session_keys)):
            one_session = session_list[i]
            if one_session["user_agent"] == user_agent:
                await redis_client.delete(session_keys[i])
                return "The session was successfully deleted"
        return "Your User Agent was not found"
    
    # инициализация и перенаправление авторизации через GitHub
    async def auth_init(self):
        """Initialize auth and redirect"""
        try:
            async with sso:
                return await sso.get_login_redirect()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auth initialization failed: {str(e)}")
        
    # проверка логина (подтверждение авторизации через GitHub)
    async def auth_callback(self, response: Response, request: Request) -> JSONResponse | str:
        async with sso:        
            github_user = await sso.verify_and_process(request)
            if not github_user:
                return "GitHub authorization failed"
        result = await self.db.execute(select(User).where(User.email == github_user.email))
        user = result.scalar_one_or_none()
        # если пользователя с такой почтой нет в базе данных, то добавляем его
        if user == None:
            if github_user.last_name != None and github_user.first_name != None:
                username = github_user.first_name + github_user.last_name
            else:
                username = github_user.display_name
            new_user = User(
                user_name=username, 
                email=github_user.email, 
                password=None, # пользователь из github не может входить по паролю
                avatar=github_user.picture
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            user = new_user

        jwt_token = create_jwt(user.user_id, user.user_role)
        response.headers["X-JWT"] = str(jwt_token)
        user_agent = request.headers.get("User-Agent")
        refresh_token = generation_refresh_token()
        
        new_session = { 
            "user_id": user.user_id,
            "user_agent": user_agent,
            "refresh_token": refresh_token,
            "refresh_token_expiretime": (datetime.now(timezone.utc)+timedelta(days=LIFETIME)).isoformat()
        }

        session_json = json.dumps(new_session)
        lifetime = LIFETIME * 24 * 60 * 60 # в секундах
        await redis_client.setex(f"session:{user.user_id}:{refresh_token}", lifetime, session_json)

        return JSONResponse({
            "message": "Authentication successful",
            "jwt_token": jwt_token,
            "session": new_session
        })