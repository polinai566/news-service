from fastapi import APIRouter, Depends
from .schemas import NewsCreate, NewsRead, NewsUpdate
from .service import NewsService
from .models import News
from app.depends import author_or_admin, same_news_author_or_admin

router = APIRouter(tags=["news"])

async def news_service(service: NewsService = Depends()) -> NewsService:
    return service

@router.post("/", response_model=NewsRead)
async def create_news(payload: NewsCreate, service: NewsService = Depends(news_service), user_id = Depends(author_or_admin)):
    return await service.create(payload, user_id)

@router.get("/", response_model=list[NewsRead])
async def get_news(service: NewsService = Depends(news_service)):
    return await service.list()

@router.get("/{news_id}", response_model=NewsRead)
async def get_news_by_id(news_id: int, service: NewsService = Depends(news_service)):
    return await service.get(news_id)

@router.put("/{news_id}", response_model=NewsRead)
async def update_news(news_id: int, payload: NewsUpdate, service: NewsService = Depends(news_service), news: News = Depends(same_news_author_or_admin)):
    return await service.update(news, payload)

@router.delete("/{news_id}", response_model=str)
async def delete_news(news_id: int, service: NewsService = Depends(news_service), news: News = Depends(same_news_author_or_admin)):
    return await service.delete(news)