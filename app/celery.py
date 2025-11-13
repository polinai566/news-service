from celery import Celery

redis_url = "redis://localhost:6379/0"

celery_app = Celery(
    "news_app",
    broker=redis_url,
    backend=redis_url,
    include=["task.email_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    task_acks_late=True,
    task_reject_on_worker_lost=True,

    worker_cancel_long_running_tasks_on_connection_loss=True,
    worker_prefetch_multiplier=1,

    task_ignore_result=False
)

celery_app.conf.task_routes = {
    "app.task.email_tasks.send_new_news_notification": {"queue": "email_notifications"},
    "app.task.email_tasks.send_weekly_digest": {"queue": "email_digest"},
}