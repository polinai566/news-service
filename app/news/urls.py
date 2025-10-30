from fastapi import APIRouter, Depends
from .schemas import NewsCreate, NewsRead, NewsUpdate
from .service import NewsService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["news"])

oauth2 = OAuth2PasswordBearer(tokenUrl="/sessions/login")

async def news_service(service: NewsService = Depends()) -> NewsService:
    return service

@router.post("/", response_model=NewsRead | str)
async def create_news(payload: NewsCreate, service: NewsService = Depends(news_service), jwt_token: str = Depends(oauth2)):
    return await service.create(payload, jwt_token)

@router.get("/", response_model=list[NewsRead] | str)
async def get_news(service: NewsService = Depends(news_service), jwt_token: str = Depends(oauth2)):
    return await service.list(jwt_token)

@router.get("/{news_id}", response_model=NewsRead | str)
async def get_news_by_id(news_id: int, service: NewsService = Depends(news_service), jwt_token: str = Depends(oauth2)):
    return await service.get(news_id, jwt_token)

@router.put("/{news_id}", response_model=NewsRead | str)
async def update_news(news_id: int, payload: NewsUpdate, service: NewsService = Depends(news_service), jwt_token: str = Depends(oauth2)):
    return await service.update(news_id, payload, jwt_token)

@router.delete("/{news_id}", response_model=None | str)
async def delete_news(news_id: int, service: NewsService = Depends(news_service), jwt_token: str = Depends(oauth2)):
    return await service.delete(news_id, jwt_token)