from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import asyncio

from prometheus_fastapi_instrumentator import Instrumentator

from .comment.urls import router as comment_router
from .news.urls import router as news_router
from .user.urls import router as user_router
from .session.urls import router as session_router
from .metrics_exporter import metrics_exporter_task
from .logging_config import setup_structlog
from .middleware.logging_middleware import LoggingMiddleware
from .hawk_config import init_hawk
from .exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # инициализация структурированного логирования
    logstash_host = os.environ["LOGSTASH_HOST"]
    logstash_port = int(os.environ["LOGSTASH_PORT"])
    setup_structlog(logstash_host=logstash_host, logstash_port=logstash_port)
    
    # запуск фоновой задачи для экспорта метрик в JSON
    metrics_task = asyncio.create_task(
        metrics_exporter_task(interval_seconds=300, metrics_dir="metrics")
    )
    app.state.metrics_task = metrics_task
    
    yield
    
    if hasattr(app.state, 'metrics_task'):
        app.state.metrics_task.cancel()
        try:
            await app.state.metrics_task
        except asyncio.CancelledError:
            pass

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)  # инициализация приложения

    # middleware для логирования запросов
    app.add_middleware(LoggingMiddleware)

    # CORS для фронтенда
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # адрес фронтенда для локальной разработки
            "http://frontend:5173",   # адрес фронтенда для Docker
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-paseto"],
    )

    # инициализация Hawk для трекинга ошибок
    hawk_dsn = os.environ.get("HAWK_DSN")
    if hawk_dsn:
        init_hawk(app, hawk_dsn)

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

    # обработчики исключений для логирования ошибок
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    return app

app = create_app()