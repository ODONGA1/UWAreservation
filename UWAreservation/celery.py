import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')

app = Celery('UWAreservation')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Optional: Configure task routes and other settings
app.conf.update(
    task_routes={
        'communications.tasks.send_email_notification': {'queue': 'emails'},
        'communications.tasks.send_sms_notification': {'queue': 'sms'},
        'communications.tasks.send_booking_reminder': {'queue': 'reminders'},
    },
    task_default_queue='default',
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
