from celery import Celery
from celery.schedules import crontab
from backend.config import config

def make_celery():
    """Create Celery instance"""
    celery = Celery(
        'parking_app',
        broker=config['default'].CELERY_BROKER_URL,
        backend=config['default'].CELERY_RESULT_BACKEND,
        include=['backend.tasks.daily_reminder', 'backend.tasks.monthly_report', 'backend.tasks.export_tasks']
    )
    
    celery.conf.update(
        result_expires=3600,
        timezone='UTC',  # Using UTC timezone
        enable_utc=True,  # Enable UTC
    )
    
    # Configure periodic tasks (times in UTC)
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'backend.tasks.daily_reminder.send_daily_reminders',
            'schedule': crontab(hour=18, minute=0),  # Every day at 6:00 PM UTC
        },
        'generate-monthly-reports': {
            'task': 'backend.tasks.monthly_report.generate_monthly_reports',
            'schedule': crontab(day_of_month=1, hour=0, minute=0),  # 1st of every month at midnight UTC
        },
    }
    
    return celery

celery = make_celery()

