import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        # генерация уникального request_id для корреляции логов
        request_id = str(uuid.uuid4())
        
        # добавление request_id в contextvars для использования в других частях приложения
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.time()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        logger.info(
            "request_started",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
            request_id=request_id
        )
        
        # выполнение запроса
        try:
            response = await call_next(request)
            status_code = response.status_code
            process_time = time.time() - start_time
            
            logger.info(
                "request_completed",
                method=method,
                path=path,
                status_code=status_code,
                process_time=round(process_time, 4),
                client_ip=client_ip,
                request_id=request_id
            )
            
            # добавление request_id в заголовок ответа для удобства отладки
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            
            logger.error(
                "request_failed",
                method=method,
                path=path,
                process_time=round(process_time, 4),
                client_ip=client_ip,
                error_type=type(exc).__name__,
                error_message=str(exc),
                request_id=request_id,
                exc_info=True
            )
            
            raise

