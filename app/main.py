from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import asyncio

from prometheus_fastapi_instrumentator import Instrumentator

from .comment.urls import router as comment_router
from .news.urls import router as news_router
from .user.urls import router as user_router
from .session.urls import router as session_router
from .metrics_exporter import metrics_exporter_task

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

    # запуск фоновой задачи для экспорта метрик в JSON
    @app.on_event("startup")
    async def startup_metrics_exporter():
        asyncio.create_task(metrics_exporter_task(interval_seconds=300, metrics_dir="metrics"))

    return app

app = create_app()