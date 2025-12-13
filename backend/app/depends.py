from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils import check_jwt
from sqlalchemy import select
from app.news.models import News
from app.comment.models import Comment
from app.database import SessionDep

oauth2 = OAuth2PasswordBearer(tokenUrl="/sessions/login")

async def get_jwt_payload(jwt_token: str = Depends(oauth2)):
    jwt_payload = check_jwt(jwt_token)
    if not jwt_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect access token")
    return jwt_payload

async def is_admin(jwt_payload: str = Depends(get_jwt_payload)):
    if jwt_payload["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
async def is_same_user(user_id: int, jwt_payload: str = Depends(get_jwt_payload)):
    if int(jwt_payload["user_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
async def same_user_or_admin(user_id: int, jwt_payload: str = Depends(get_jwt_payload)):
    if jwt_payload["user_role"] != "admin" and int(jwt_payload["user_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
async def author_or_admin(jwt_payload: str = Depends(get_jwt_payload)):
    if jwt_payload["user_role"] != "admin" and jwt_payload["user_role"] != "author":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return int(jwt_payload["user_id"])
    
async def same_news_author_or_admin(news_id: int, db: SessionDep, jwt_payload: str = Depends(get_jwt_payload)):
    news = await db.execute(select(News).where(News.news_id == news_id))
    news = news.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    if jwt_payload["user_role"] != "admin" and int(jwt_payload["user_id"]) != news.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return news
    
async def same_comment_author_or_admin(comment_id: int, db: SessionDep, jwt_payload: str = Depends(get_jwt_payload)):
    comment = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = comment.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if jwt_payload["user_role"] != "admin" and int(jwt_payload["user_id"]) != comment.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return comment