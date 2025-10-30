from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import select

from app.database import SessionDep
from app.user.models import User
from .models import News
from .schemas import NewsCreate, NewsUpdate

class NewsService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание новости
    async def create(self, payload: NewsCreate) -> News:
        # проверка существования и верифицированности автора
        author = await self.db.execute(select(User).where(User.user_id == payload.author_id))
        author = author.scalar_one_or_none()
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        if not author.is_verified: # type: ignore
            raise HTTPException(status_code=400, detail="Author is not verified")

        # добавление новости
        new_news = News(**payload.model_dump())
        self.db.add(new_news)
        await self.db.commit()
        await self.db.refresh(new_news)
        return new_news
    
    # чтение списка новостей
    async def list(self) -> Sequence[News]:
        news = await self.db.execute(select(News))
        return news.scalars().all()
    
    # чтение новости по индексу
    async def get(self, news_id: int) -> News:
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        return news
    
    # обновление новости
    async def update(self, news_id: int, payload: NewsUpdate) -> News:
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(news, field, value)
        
        await self.db.commit()
        await self.db.refresh(news)
        return news

    # удаление пользователя
    async def delete(self, news_id: int) -> None:
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        await self.db.delete(news)
        await self.db.commit()