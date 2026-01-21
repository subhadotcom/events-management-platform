"""
Celery tasks for scheduled email notifications.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Enrollment, EnrollmentStatus


@shared_task
def send_enrollment_followup_email():
    """
    Send follow-up email to seekers who enrolled 1 hour ago.
    Scheduled to run every 5 minutes.
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    
    # Get enrollments created between 1 hour and 55 minutes ago
    recent_enrollments = Enrollment.objects.filter(
        status=EnrollmentStatus.ENROLLED,
        created_at__gte=one_hour_ago,
        created_at__lte=five_minutes_ago
    ).select_related('seeker', 'event')
    
    emails_sent = 0
    
    for enrollment in recent_enrollments:
        try:
            subject = f'Thank you for enrolling in {enrollment.event.title}'
            message = f"""
            Hi,
            
            Thank you for enrolling in "{enrollment.event.title}"!
            
            Event Details:
            - Date: {enrollment.event.starts_at.strftime('%B %d, %Y at %I:%M %p')}
            - Location: {enrollment.event.location}
            - Language: {enrollment.event.language}
            
            We're excited to see you there!
            
            Best regards,
            Events Platform Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [enrollment.seeker.email],
                fail_silently=True,
            )
            
            emails_sent += 1
            
        except Exception as e:
            print(f"Error sending follow-up email: {str(e)}")
            continue
    
    return f"Sent {emails_sent} follow-up emails"


@shared_task
def send_event_reminder_email():
    """
    Send reminder email to seekers 1 hour before their enrolled event.
    Scheduled to run every 5 minutes.
    """
    one_hour_from_now = timezone.now() + timedelta(hours=1)
    fifty_five_minutes_from_now = timezone.now() + timedelta(minutes=55)
    
    # Get enrollments for events starting in about 1 hour
    upcoming_enrollments = Enrollment.objects.filter(
        status=EnrollmentStatus.ENROLLED,
        event__starts_at__gte=fifty_five_minutes_from_now,
        event__starts_at__lte=one_hour_from_now
    ).select_related('seeker', 'event')
    
    emails_sent = 0
    
    for enrollment in upcoming_enrollments:
        try:
            subject = f'Reminder: {enrollment.event.title} starts in 1 hour!'
            message = f"""
            Hi,
            
            This is a reminder that your event "{enrollment.event.title}" is starting soon!
            
            Event Details:
            - Starts at: {enrollment.event.starts_at.strftime('%B %d, %Y at %I:%M %p')}
            - Location: {enrollment.event.location}
            - Language: {enrollment.event.language}
            
            See you there!
            
            Best regards,
            Events Platform Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [enrollment.seeker.email],
                fail_silently=True,
            )
            
            emails_sent += 1
            
        except Exception as e:
            print(f"Error sending reminder email: {str(e)}")
            continue
    
    return f"Sent {emails_sent} reminder emails"
