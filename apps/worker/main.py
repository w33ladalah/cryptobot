from celery import Celery
from config.settings import config
from tasks.data_sources import pull_platform_from_coingecko

# Initialize Celery app
app = Celery(
    'crypto_bot',
    broker=config.CELERY_BROKER_URL,
    result_backend=config.CELERY_RESULT_BACKEND
)
