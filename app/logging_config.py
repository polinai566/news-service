import logging
import sys
import os
import structlog
from structlog.types import Processor


def add_logstash_handler(logger: logging.Logger, logstash_host: str = "localhost", logstash_port: int = 5000):
    try:
        from logging.handlers import SocketHandler
        class JSONSocketHandler(SocketHandler):
            def makePickle(self, record):
                message = self.format(record)
                return (message + '\n').encode('utf-8')
        socket_handler = JSONSocketHandler(logstash_host, logstash_port)
        socket_handler.setLevel(logging.INFO)
        socket_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(socket_handler)
    except Exception as e:
        print(f"Не удалось подключиться к Logstash: {e}")


def setup_structlog(logstash_host: str = None, logstash_port: int = 5000) -> structlog.BoundLogger:
    # процессоры для structlog
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # добавление JSON-процессора для вывода
    if os.getenv("LOG_FORMAT", "json") == "json":
        processors.append(structlog.processors.JSONRenderer(ensure_ascii=False))
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # настройка structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # настройка стандартного logging для интеграции с structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # при указании logstash_host добавляем handler для отправки в Logstash
    if logstash_host:
        root_logger = logging.getLogger()
        add_logstash_handler(root_logger, logstash_host, logstash_port)
    
    return structlog.get_logger()

# получение настроенного logger
def get_logger(name: str = __name__) -> structlog.BoundLogger:
    return structlog.get_logger(name)

