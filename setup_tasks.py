"""
Setup script for scheduled tasks using Django Celery Beat.
Run this script to create periodic tasks for email notifications.

Usage:
    python setup_tasks.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'events_platform.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json


def setup_tasks():
    """Create periodic tasks for email notifications"""
    
    # Create interval schedule - every 5 minutes
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=5,
        period=IntervalSchedule.MINUTES,
    )
    
    if created:
        print("✓ Created interval schedule: Every 5 minutes")
    else:
        print("✓ Interval schedule already exists")
    
    # Create follow-up email task
    task1, created1 = PeriodicTask.objects.get_or_create(
        name='Send enrollment follow-up emails',
        defaults={
            'interval': schedule,
            'task': 'events.tasks.send_enrollment_followup_email',
            'enabled': True,
        }
    )
    
    if created1:
        print("✓ Created task: Send enrollment follow-up emails")
    else:
        print("✓ Task already exists: Send enrollment follow-up emails")
    
    # Create reminder email task
    task2, created2 = PeriodicTask.objects.get_or_create(
        name='Send event reminder emails',
        defaults={
            'interval': schedule,
            'task': 'events.tasks.send_event_reminder_email',
            'enabled': True,
        }
    )
    
    if created2:
        print("✓ Created task: Send event reminder emails")
    else:
        print("✓ Task already exists: Send event reminder emails")
    
    print("\n✅ Setup complete! Celery Beat will now run these tasks every 5 minutes.")
    print("\nMake sure Celery worker and beat are running:")
    print("  1. celery -A events_platform worker -l info")
    print("  2. celery -A events_platform beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler")


if __name__ == '__main__':
    setup_tasks()
