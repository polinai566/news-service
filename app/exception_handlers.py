from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

logger = structlog.get_logger(__name__)

# обработчик для HTTP исключений (4xx, 5xx)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
        request_id=structlog.contextvars.get_contextvars().get("request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# обработчик для ошибок валидации Pydantic
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method,
        request_id=structlog.contextvars.get_contextvars().get("request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# обработчик всех оставшихся исключений
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
        request_id=structlog.contextvars.get_contextvars().get("request_id", "unknown"),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


