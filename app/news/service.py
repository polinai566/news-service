from typing import Sequence
from sqlalchemy import select

from app.database import SessionDep
from .models import News
from .schemas import NewsCreate, NewsUpdate
from app.utils import check_jwt, get_privileges

class NewsService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание новости
    async def create(self, payload: NewsCreate, jwt_token: str) -> News | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        if jwt_payload["user_role"] in ("admin", "author"):
            new_news = News(**payload.model_dump(), author_id = int(jwt_payload["user_id"]))
            self.db.add(new_news)
            await self.db.commit()
            await self.db.refresh(new_news)
            return new_news
        else:
            return "Permission denied"
    
    # чтение списка новостей
    async def list(self, jwt_token: str) -> Sequence[News] | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        news = await self.db.execute(select(News))
        return news.scalars().all()
    
    # чтение новости по индексу
    async def get(self, news_id: int, jwt_token: str) -> News | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            return "News not found"
        return news
    
    # обновление новости
    async def update(self, news_id: int, payload: NewsUpdate, jwt_token: str) -> News | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            return "News not found"
        rights = get_privileges(jwt_payload, news.author_id) # type: ignore
        if rights in ["admin", "author_same"]:
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(news, field, value)
            await self.db.commit()
            await self.db.refresh(news)
            return news
        else:
            return "Permission denied"
        
    # удаление новости
    async def delete(self, news_id: int, jwt_token: str) -> None | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            return "News not found"
        rights = get_privileges(jwt_payload, news.author_id) # type: ignore
        if rights in ["admin", "author_same"]:
            await self.db.delete(news)
            await self.db.commit()
            return "The news was successfully deleted"
        return "Permission denied"