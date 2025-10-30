from fastapi import APIRouter, Depends
from .schemas import NewsCreate, NewsRead, NewsUpdate
from .service import NewsService

router = APIRouter(tags=["news"])

async def news_service(service: NewsService = Depends()) -> NewsService:
    return service

@router.post("/", response_model=NewsRead)
async def create_news(payload: NewsCreate, service: NewsService = Depends(news_service)):
    return await service.create(payload)

@router.get("/", response_model=list[NewsRead])
async def get_news(service: NewsService = Depends(news_service)):
    return await service.list()

@router.get("/{news_id}", response_model=NewsRead)
async def get_news_by_id(news_id: int, service: NewsService = Depends(news_service)):
    return await service.get(news_id)

@router.put("/{news_id}", response_model=NewsRead)
async def update_news(news_id: int, payload: NewsUpdate, service: NewsService = Depends(news_service)):
    return await service.update(news_id, payload)

# удаление новости (delete)
@router.delete("/{news_id}")
async def delete_news(news_id: int, service: NewsService = Depends(news_service)):
    return await service.delete(news_id)