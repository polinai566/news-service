from time import timezone
from celery import Celery
from celery.schedules import crontab
from app.database import SyncSession, sync_redis_client
from app.user.models import User
from app.news.models import News
from app.comment.models import Comment
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import logging
import os
import time
from app.metrics import (
    notifications_sent_total,
    notifications_failed_total,
    notification_duration_seconds
)

app = Celery('celery', broker='redis://localhost:6379')
app.conf.timezone = 'Europe/Moscow'

# настройка ретраев
app.conf.task_default_retry_delay = 10  # задержка перед первым ретраем (секунды)
app.conf.task_max_retries = 3  # максимальное количество попыток
app.conf.task_retry_backoff = True  # включение экспоненциальной задержки
app.conf.task_retry_backoff_max = 300  # максимальная задержка (5 минут)

# настройка cron
app.conf.beat_schedule = {
    'weekly-digest-every-sunday': {
        'task': 'app.celery.send_weekly_digest',
        'schedule': crontab(hour=18, minute=43, day_of_week=5),  # Каждое воскресенье в 0:00
    },
}

# настройка логирования
def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, 'celery_tasks.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger = logging.getLogger('celery_tasks')
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger

logger = setup_logging()

# общие настройки для всех задач celery 
def common_task_settings(**overrides):
    default_settings = {
        'bind': True,
        'max_retries': 5,
        'default_retry_delay': 30,
        'retry_backoff': True,
        'retry_backoff_max': 600,
        'retry_jitter': True,
        'acks_late': True,
        'reject_on_worker_lost': True,
    }
    default_settings.update(overrides)
    return app.task(**default_settings)

@common_task_settings()
def send_notification_of_new_news(self, news_id):
    key = f"news_notification:{news_id}"
    if sync_redis_client.exists(key): # проверка идемпотентности
        logger.info(f"Уведомление о новости {news_id} уже было отправлено.")
        return
    start_time = time.time()
    notification_type = 'new_news'
    try:
        with SyncSession() as db:
            users = db.execute(select(User))
            user_list = users.scalars().all()
            for user in user_list:
                message = f"На почту '{user.email}' отправлено уведомление о публикации новой новости (ID: {news_id})."
                logger.info(message)
            sync_redis_client.setex(key, 86400, "sent") # хранение в кэше - 24 часа
            # инкремент метрики успешной отправки
            notifications_sent_total.labels(notification_type=notification_type).inc()
            # запись времени выполнения
            duration = time.time() - start_time
            notification_duration_seconds.labels(notification_type=notification_type).observe(duration)
                
    except SQLAlchemyError as exc:
        logger.error(f"Ошибка базы данных: {exc}")
        # инкремент метрики неудачной отправки
        notifications_failed_total.labels(notification_type=notification_type, error_type='database').inc()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except Exception as exc:
        logger.error(f"Ошибка: {exc}")
        # инкремент метрики неудачной отправки
        notifications_failed_total.labels(notification_type=notification_type, error_type='general').inc()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@common_task_settings()
def send_weekly_digest(self):
    week_key = datetime.now(timezone.utc).strftime("%Y-%U") # уникальный ключ: год-неделя
    key = f"weekly_digest:{week_key}"
    if sync_redis_client.exists(key): # проверка идемпотентности
        logger.info(f"Еженедельный дайджест для недели {week_key} уже был отправлен.")
        return
    start_time = time.time()
    notification_type = 'weekly_digest'
    try:
        with SyncSession() as db:
            users = db.execute(select(User))
            user_list = users.scalars().all()
            for user in user_list:
                message = f"На почту '{user.email}' отправлен еженедельный дайджест с новостями за неделю."
                logger.info(message)
            sync_redis_client.setex(key, 691200, "sent") # хранение - 8 дней (> недели)
            # инкремент метрики успешной отправки
            notifications_sent_total.labels(notification_type=notification_type).inc()
            # запись времени выполнения
            duration = time.time() - start_time
            notification_duration_seconds.labels(notification_type=notification_type).observe(duration)

    except SQLAlchemyError as exc:
        logger.error(f"Ошибка базы данных в еженедельном дайджесте: {exc}")
        # инкремент метрики неудачной отправки
        notifications_failed_total.labels(notification_type=notification_type, error_type='database').inc()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except Exception as exc:
        logger.error(f"Ошибка в еженедельном дайджесте: {exc}")
        # инкремент метрики неудачной отправки
        notifications_failed_total.labels(notification_type=notification_type, error_type='general').inc()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# graceful shutdown обработчики
def worker_ready_handler(sender=None, **kwargs):
    logger.info("Celery worker запущен и готов к работе")

def worker_shutdown_handler(sender=None, **kwargs):
    logger.info("Celery worker успешно завершает работу...")

def setup_graceful_shutdown():
    # обработчики вызваются при запуске и завершении воркера
    from celery.signals import worker_ready, worker_shutdown
    
    worker_ready.connect(worker_ready_handler)
    worker_shutdown.connect(worker_shutdown_handler)

# инициализация graceful shutdown
setup_graceful_shutdown()