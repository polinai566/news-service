from fastapi import Response, Request, HTTPException
from typing import Sequence
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import SessionDep
from app.user.models import User
from app.user.schemas import UserLogin
from .schemas import SessionRefreshToken
from app.utils import check_password, create_jwt, generation_refresh_token, check_jwt, get_privileges, sso
from .models import Session
from fastapi.responses import JSONResponse

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
    async def put(self, payload: SessionRefreshToken, response: Response, request: Request) -> Session | str:
        user_agent = request.headers.get("User-Agent")
        session = await self.db.execute(
            select(Session).where(
                (Session.refresh_token == payload.refresh_token) & 
                (Session.user_agent == user_agent)
            )
        )
        session = session.scalar_one_or_none()
        if not session:
            return "User-Agent or Refresh token is invalid"
        if datetime.now(timezone.utc) > session.refresh_token_expiretime: # type: ignore
            await self.db.delete(session)
            await self.db.commit()
            return "The session expired. Log in again"
        user = await self.db.execute(select(User).where(User.user_id == session.user_id))
        user = user.scalar_one_or_none()
        if not user:
            return "Refresh token not linked to user"
        refresh_token = generation_refresh_token()
        jwt_token = create_jwt(session.user_id, user.user_role) # type: ignore
        response.headers["X-JWT"] = str(jwt_token)
        new_session = Session(
            refresh_token=refresh_token,
            user_id=session.user_id,
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

        jwt_token = create_jwt(user.user_id, user.user_role) # type: ignore
        response.headers["X-JWT"] = str(jwt_token)
        user_agent = request.headers.get("User-Agent")
        refresh_token = generation_refresh_token()
        new_session = Session(
            refresh_token=refresh_token,
            user_id=user.user_id,
            user_agent=user_agent
        )

        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        return JSONResponse({
            "message": "Authentication successful",
            "jwt_token": jwt_token,
            "session": {
                "refresh_token": new_session.refresh_token,
                "session_id": new_session.session_id,
                "user_id": new_session.user_id,
                "refresh_token_expiretime": str(new_session.refresh_token_expiretime),
                "user_agent": new_session.user_agent
            }
        })