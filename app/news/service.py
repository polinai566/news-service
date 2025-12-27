from typing import Sequence
from sqlalchemy import select
from fastapi import HTTPException, status
from app.database import SessionDep, redis_client
from .models import News
from .schemas import NewsCreate, NewsUpdate, NewsRead
import app.celery as task
from app.metrics import news_created_total
from app.logging_config import get_logger

import json

logger = get_logger(__name__)

class NewsService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание новости
    async def create(self, payload: NewsCreate, user_id: int) -> News:
        new_news = News(**payload.model_dump(), author_id = user_id)
        self.db.add(new_news)
        await self.db.commit()
        await self.db.refresh(new_news)
        await redis_client.delete("news_list_all")
        # инкремент метрики создания новости
        news_created_total.labels(author_id=str(user_id)).inc()
        task.send_notification_of_new_news(new_news.news_id)
        return new_news
    
    # чтение списка новостей
    async def list(self) -> Sequence[NewsRead]:
        cached_news_list = await redis_client.get("news_list_all")
        if cached_news_list:
            news_list_data = json.loads(cached_news_list)
            logger.info("news_list_from_cache", source="cache")
            return [NewsRead.model_validate(news_data) for news_data in news_list_data]
        news = await self.db.execute(select(News))
        news_list = news.scalars().all()
        if not news_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No news found")
        news_data_list = [NewsRead.model_validate(news) for news in news_list]
        news_list_data = [news_data.model_dump(mode='json') for news_data in news_data_list]
        news_list_json = json.dumps(news_list_data)
        await redis_client.setex("news_list_all", 300, news_list_json) # TTL 5 минут = 300 секунд
        logger.info("news_list_from_database", source="database", count=len(news_data_list))
        return news_data_list
    
    # чтение новости по индексу
    async def get(self, news_id: int) -> NewsRead:
        cached_news = await redis_client.get(f"news_{news_id}")
        if cached_news:
            news_dict = json.loads(cached_news) # десериализация данных из JSON
            news_data = NewsRead.model_validate(news_dict)
            logger.info("news_from_cache", news_id=news_id, source="cache")
            return news_data
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
        news_data = NewsRead.model_validate(news)
        news_json = news_data.model_dump_json() # сериализация данных в JSON
        await redis_client.setex(f"news_{news_id}", 300, news_json) # TTL 5 минут = 300 секунд
        logger.info("news_from_database", news_id=news_id, source="database")
        return news_data
    
    # обновление новости
    async def update(self, news_id: int, news: News, payload: NewsUpdate) -> News:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(news, field, value)
        await self.db.commit()
        await self.db.refresh(news)
        await redis_client.delete(f"news_{news_id}")
        await redis_client.delete("news_list_all")
        return news
        
    # удаление новости
    async def delete(self, news_id: int, news: News) -> str:
        await self.db.delete(news)
        await self.db.commit()
        await redis_client.delete(f"news_{news_id}")
        await redis_client.delete("news_list_all")
        return "The news was successfully deleted"