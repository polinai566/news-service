from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy import select

from app.database import SessionDep
from .models import News
from .schemas import NewsCreate, NewsUpdate, NewsRead

class NewsService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание новости
    async def create(self, payload: NewsCreate, user_id: int) -> News:
        new_news = News(**payload.model_dump(), author_id = user_id)
        self.db.add(new_news)
        await self.db.commit()
        await self.db.refresh(new_news)
        return new_news
    
    # чтение списка новостей
    async def list(self) -> Sequence[News]:
        news = await self.db.execute(select(News))
        news_list = news.scalars().all()
        if not news_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No news found")
        return news_list
    
    # чтение новости по индексу
    async def get(self, news_id: int) -> News:
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
        return news
    
    # обновление новости
    async def update(self, news: News, payload: NewsUpdate) -> News:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(news, field, value)
        await self.db.commit()
        await self.db.refresh(news)
        return news

    # удаление новости
    async def delete(self, news: News) -> str:
        await self.db.delete(news)
        await self.db.commit()
        return "The news was successfully deleted"