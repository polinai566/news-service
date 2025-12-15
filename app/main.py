from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from prometheus_fastapi_instrumentator import Instrumentator

from .comment.urls import router as comment_router
from .news.urls import router as news_router
from .user.urls import router as user_router
from .session.urls import router as session_router

def create_app() -> FastAPI:
    app = FastAPI()  # инициализация приложения

    # CORS для фронтенда
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # адрес фронтенда
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-jwt"],
    )

    # статика для обложек новостей
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # основные роутеры доменной логики
    app.include_router(user_router, prefix="/user")
    app.include_router(news_router, prefix="/news")
    app.include_router(comment_router, prefix="/comment")
    app.include_router(session_router, prefix="/session")

    # базовые метрики Prometheus + эндпоинт /metrics
    Instrumentator().instrument(app).expose(app)

    return app

app = create_app()