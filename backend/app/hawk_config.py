from typing import Optional
from hawk_python_sdk.modules.fastapi import HawkFastapi
import structlog

logger = structlog.get_logger(__name__)
_hawk_client = None

def init_hawk(app, dsn):
    global _hawk_client
    
    if _hawk_client is not None:
        return _hawk_client
    
    if not dsn:
        logger.warning("Hawk DSN не указан, Hawk не будет инициализирован")
        return None
    
    try:
        _hawk_client = HawkFastapi({
            'app_instance': app,
            'token': dsn
        })
        logger.info("Hawk успешно инициализирован")
        return _hawk_client
    except ImportError as e:
        logger.error(f"Не удалось импортировать hawk-python-sdk: {e}")
        return None
    except Exception as e:
        logger.error(f"Ошибка инициализации Hawk: {e}")
        return None

def get_hawk_client():
    return _hawk_client

def capture_exception(exc: Exception, context: Optional[dict] = None):
    client = get_hawk_client()
    if client is None:
        logger.warning("Hawk клиент не инициализирован, ошибка не отправлена")
        return
    
    try:
        if context:
            client.send(exc, context=context)
        else:
            client.send(exc)
        logger.debug("Исключение отправлено в Hawk")
    except Exception as e:
        logger.error(f"Ошибка при отправке в Hawk: {e}")
