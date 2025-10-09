from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.database import SessionDep
from app.news.schemas import NewsCreate, NewsRead, NewsUpdate
from app.news.models import News
from app.user.models import User

router = APIRouter(tags=["news"])

# создание новости (create)
@router.post("/", response_model=NewsRead)
async def create_news(news: NewsCreate, db: SessionDep):
    # проверка существования и верифицированности автора
    author = await db.execute(select(User).where(User.user_id == news.author_id))
    author = author.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not author.is_verified:
        raise HTTPException(status_code=400, detail="Author is not verified")

    # добавление новости
    new_news = News(**news.model_dump())
    db.add(new_news)
    await db.commit()
    await db.refresh(new_news)
    return new_news

# чтение списка новостей (read)
@router.get("/", response_model=list[NewsRead])
async def get_news(db: SessionDep):
    news = await db.execute(select(News))
    return news.scalars().all()

# чтение новости по индексу (read)
@router.get("/{news_id}", response_model=NewsRead)
async def get_news_by_id(news_id: int, db: SessionDep):
    news = await db.execute(select(News).where(News.news_id == news_id))
    news = news.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

# обновление новости (update)
@router.put("/{news_id}", response_model=NewsRead)
async def update_news(news_id: int, news_update: NewsUpdate, db: SessionDep):
    news = await db.execute(select(News).where(News.news_id == news_id))
    news = news.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    for field, value in news_update.model_dump(exclude_unset=True).items():
        setattr(news, field, value)
    
    await db.commit()
    await db.refresh(news)
    return news

# удаление новости (delete)
@router.delete("/{news_id}")
async def delete_news(news_id: int, db: SessionDep):
    news = await db.execute(select(News).where(News.news_id == news_id))
    news = news.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    await db.delete(news)
    await db.commit()
    return {"message": "News deleted successfully"}