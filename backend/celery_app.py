import os
from datetime import datetime
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab

load_dotenv()

celery = Celery(
    'hospital_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery.conf.update(
    timezone='Asia/Kolkata',
    enable_utc=False,
    worker_pool='solo',
)

celery.conf.beat_schedule = {
   
    'send-all-doctors-monthly-reports': {
        'task': 'tasks.send_all_doctors_monthly_reports',
        'schedule': crontab(minute=20, hour=22, day_of_month=30),
    },
  
            'send-daily-appointment-reminders': {
                'task': 'tasks.send_daily_reminders',
                'schedule': crontab(minute=20, hour=22),
            },
}

celery.autodiscover_tasks(['tasks'])

