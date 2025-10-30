from fastapi import FastAPI
import logging

from .comment.urls import router as comment_router
from .news.urls import router as news_router
from .user.urls import router as user_router
from .session.urls import router as session_router

app = FastAPI() # инициализация приложения

app.include_router(user_router, prefix="/user")
app.include_router(news_router, prefix="/news")
app.include_router(comment_router, prefix="/comment")
app.include_router(session_router, prefix="/session")

logging.basicConfig()    
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)