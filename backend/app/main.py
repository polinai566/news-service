from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .comment.urls import router as comment_router
from .news.urls import router as news_router
from .user.urls import router as user_router
from .session.urls import router as session_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],  # адрес фронтенда
    allow_origins=["http://frontend:5173"],  # адрес фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-jwt"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
# папка с обложками для новостей
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(user_router, prefix="/user")
app.include_router(news_router, prefix="/news")
app.include_router(comment_router, prefix="/comment")
app.include_router(session_router, prefix="/session")
