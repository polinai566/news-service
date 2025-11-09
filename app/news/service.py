from typing import Sequence
from sqlalchemy import select

from app.database import SessionDep, redis_client
from .models import News
from .schemas import NewsCreate, NewsUpdate, NewsRead
from app.utils import check_jwt, get_privileges

import json

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
    async def list(self, jwt_token: str) -> Sequence[NewsRead] | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        cached_news_list = redis_client.get("news_list_all")
        if cached_news_list:
            news_list_data = json.loads(cached_news_list)
            return [NewsRead.model_validate(news_data) for news_data in news_list_data]
        news = await self.db.execute(select(News))
        news_list = news.scalars().all()
        if not news_list:
            return "No news found"
        news_data_list = [NewsRead.model_validate(news) for news in news_list]
        news_list_data = [news_data.model_dump(mode='json') for news_data in news_data_list]
        news_list_json = json.dumps(news_list_data)
        redis_client.setex("news_list_all", 300, news_list_json) # TTL 5 минут = 300 секунд
        return news_data_list
    
    # чтение новости по индексу
    async def get(self, news_id: int, jwt_token: str) -> NewsRead | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect token"
        cached_news = redis_client.get(f"news_{news_id}")
        if cached_news:
            news_dict = json.loads(cached_news) # десериализация данных из JSON
            news_data = NewsRead.model_validate(news_dict)
            return news_data
        news = await self.db.execute(select(News).where(News.news_id == news_id))
        news = news.scalar_one_or_none()
        if not news:
            return "News not found"
        news_data = NewsRead.model_validate(news)
        news_json = news_data.model_dump_json() # сериализация данных в JSON
        redis_client.setex(f"news_{news_id}", 300, news_json) # TTL 5 минут = 300 секунд
        return news_data
    
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
            redis_client.delete(f"news_{news_id}")
            redis_client.delete("news_list_all")
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
            redis_client.delete(f"news_{news_id}")
            redis_client.delete("news_list_all")
            return "The news was successfully deleted"
        return "Permission denied"