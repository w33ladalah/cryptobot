from celery import Celery
from celery.schedules import crontab
from config.settings import config

# Initialize Celery app
app = Celery(
    'crypto_bot',
    broker=config.CELERY_BROKER_URL,
    result_backend=config.CELERY_RESULT_BACKEND
)

# app.conf.beat_schedule = {
#     'run-every-5-minutes': {
#         'task': 'crypto_bot.run_bot_task',
#         'schedule': crontab(minute='*/5'),
#     },
# }
