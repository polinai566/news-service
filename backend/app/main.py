from fastapi import FastAPI

from .comment.urls import router as comment_router
from .news.urls import router as news_router
from .user.urls import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/user")
app.include_router(news_router, prefix="/news")
app.include_router(comment_router, prefix="/comment")
