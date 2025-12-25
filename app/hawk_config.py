from typing import Optional
import structlog

logger = structlog.get_logger(__name__)
_hawk_client = None

def init_hawk(dsn: str = None):
    global _hawk_client
    
    if _hawk_client is not None:
        return _hawk_client
    
    if not dsn:
        logger.warning("Hawk DSN не указан, Hawk не будет инициализирован")
        return None
    
    try:
        from hawk_python_sdk import Hawk
        _hawk_client = Hawk()
        _hawk_client.init(dsn=dsn)
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
            client.capture(exc, context=context)
        else:
            client.capture(exc)
        logger.debug("Исключение отправлено в Hawk")
    except Exception as e:
        logger.error(f"Ошибка при отправке в Hawk: {e}")
