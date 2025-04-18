import sys
from pathlib import Path

# Add the 'apps' directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

from celery import Celery
from config.settings import config

# Initialize Celery app
app = Celery(
    'crypto_bot',
    broker=config.CELERY_BROKER_URL,
    result_backend=config.CELERY_RESULT_BACKEND
)

# Autodiscover tasks from the 'tasks' module
app.autodiscover_tasks(['tasks'])

# app.conf.beat_schedule = {
#     'run-every-5-minutes': {
#         'task': 'crypto_bot.run_bot_task',
#         'schedule': crontab(minute='*/5'),
#     },
# }
