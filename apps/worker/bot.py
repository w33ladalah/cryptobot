from celery import Celery
from celery.schedules import crontab

"""
Author: Hendro Wibowo
Date: 2025-01-08
"""
app = Celery('bot')
app.conf.broker_url = 'redis://localhost:6379/0'

@app.task
def run_bot_task():
    # Your bot logic here
    pass

app.conf.beat_schedule = {
    'run-every-5-minutes': {
        'task': 'bot.run_bot_task',
        'schedule': crontab(minute='*/5'),
    },
}
