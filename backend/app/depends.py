from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils import check_paseto_token
from sqlalchemy import select
from app.news.models import News
from app.comment.models import Comment
from app.database import SessionDep

oauth2 = OAuth2PasswordBearer(tokenUrl="/sessions/login")

async def get_paseto_payload(paseto_token: str = Depends(oauth2)):
    payload = check_paseto_token(paseto_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect access token")
    return payload

async def is_admin(paseto_payload: str = Depends(get_paseto_payload)):
    if paseto_payload["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
async def is_same_user(user_id: int, paseto_payload: str = Depends(get_paseto_payload)):
    if int(paseto_payload["user_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
async def same_user_or_admin(user_id: int, paseto_payload: str = Depends(get_paseto_payload)):
    if paseto_payload["user_role"] != "admin" and int(paseto_payload["user_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
async def author_or_admin(paseto_payload: str = Depends(get_paseto_payload)):
    if paseto_payload["user_role"] != "admin" and paseto_payload["user_role"] != "author":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return int(paseto_payload["user_id"])
    
async def same_news_author_or_admin(news_id: int, db: SessionDep, paseto_payload: str = Depends(get_paseto_payload)):
    news = await db.execute(select(News).where(News.news_id == news_id))
    news = news.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    if paseto_payload["user_role"] != "admin" and int(paseto_payload["user_id"]) != news.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return news
    
async def same_comment_author_or_admin(comment_id: int, db: SessionDep, paseto_payload: str = Depends(get_paseto_payload)):
    comment = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = comment.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if paseto_payload["user_role"] != "admin" and int(paseto_payload["user_id"]) != comment.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return comment