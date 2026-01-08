from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from .models import Enrollment, Event

@shared_task
def send_followup_emails():
    # Send to seekers who enrolled 1 hour ago
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)
    # Window of 5 minutes to avoid double sending or missing (assuming task runs every 5 mins)
    # Better approach: Flag enrollment as 'followup_sent'
    # But schema doesn't have it. I'll use time window for now.
    window_start = one_hour_ago - timedelta(minutes=5)
    
    enrollments = Enrollment.objects.filter(
        created_at__gte=window_start,
        created_at__lte=one_hour_ago,
        status='ENROLLED'
    )
    
    for enrollment in enrollments:
        print(f"Sending follow-up to {enrollment.seeker.email}")
        send_mail(
            'How was your enrollment?',
            f'You enrolled in {enrollment.event.title} 1 hour ago.',
            'noreply@events.com',
            [enrollment.seeker.email],
            fail_silently=True,
        )

@shared_task
def send_reminder_emails():
    # Send to seekers 1 hour before event starts
    now = timezone.now()
    one_hour_future = now + timedelta(hours=1)
    window_end = one_hour_future + timedelta(minutes=5)
    
    events = Event.objects.filter(
        starts_at__gte=one_hour_future,
        starts_at__lte=window_end
    )
    
    for event in events:
        enrollments = event.enrollments.filter(status='ENROLLED')
        for enrollment in enrollments:
            print(f"Sending reminder to {enrollment.seeker.email}")
            send_mail(
                'Event Reminder',
                f'Your event {event.title} starts in 1 hour.',
                'noreply@events.com',
                [enrollment.seeker.email],
                fail_silently=True,
            )
