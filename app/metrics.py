from prometheus_client import Counter, Histogram

# метрика для отслеживания количества созданных новостей
news_created_total = Counter(
    'news_created_total',
    'Общее количество созданных новостей',
    labelnames=['author_id']
)

# метрика для отслеживания количества зарегистрированных пользователей
users_registered_total = Counter(
    'users_registered_total',
    'Общее количество зарегистрированных пользователей'
)

# метрика для отслеживания успешных отправок уведомлений
notifications_sent_total = Counter(
    'notifications_sent_total',
    'Общее количество успешно отправленных уведомлений',
    labelnames=['notification_type']  # 'new_news' или 'weekly_digest'
)

# метрика для отслеживания неудачных отправок уведомлений
notifications_failed_total = Counter(
    'notifications_failed_total',
    'Общее количество неудачных попыток отправки уведомлений',
    labelnames=['notification_type', 'error_type']
)

# метрика для отслеживания времени отправки уведомлений
notification_duration_seconds = Histogram(
    'notification_duration_seconds',
    'Время отправки уведомлений в секундах',
    labelnames=['notification_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)


