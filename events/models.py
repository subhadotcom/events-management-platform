"""
Models for the events app.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    """Event model"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    language = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    capacity = models.IntegerField(null=True, blank=True, help_text="Max number of enrollments (optional)")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events',
        limit_choices_to={'profile__role': 'Facilitator'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['starts_at']
        indexes = [
            models.Index(fields=['starts_at']),
            models.Index(fields=['language']),
            models.Index(fields=['location']),
            models.Index(fields=['created_by']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.starts_at}"

    def clean(self):
        """Validate event dates"""
        if self.ends_at and self.starts_at and self.ends_at <= self.starts_at:
            raise ValidationError('End time must be after start time')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_past(self):
        """Check if event has ended"""
        return timezone.now() > self.ends_at

    @property
    def is_upcoming(self):
        """Check if event is upcoming"""
        return timezone.now() < self.starts_at

    @property
    def total_enrollments(self):
        """Get total active enrollments"""
        return self.enrollments.filter(status='enrolled').count()

    @property
    def available_seats(self):
        """Get available seats (None if no capacity limit)"""
        if self.capacity is None:
            return None
        return max(0, self.capacity - self.total_enrollments)

    @property
    def is_full(self):
        """Check if event is at capacity"""
        if self.capacity is None:
            return False
        return self.total_enrollments >= self.capacity


class EnrollmentStatus(models.TextChoices):
    """Enrollment status choices"""
    ENROLLED = 'enrolled', 'Enrolled'
    CANCELED = 'canceled', 'Canceled'


class Enrollment(models.Model):
    """Enrollment model for seekers"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='enrollments')
    seeker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'profile__role': 'Seeker'}
    )
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ENROLLED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollments'
        ordering = ['-created_at']
        unique_together = [['event', 'seeker']]
        indexes = [
            models.Index(fields=['seeker', 'status']),
            models.Index(fields=['event', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.seeker.email} - {self.event.title} ({self.status})"

    def clean(self):
        """Validate enrollment"""
        # Check if event is full
        if self.event.is_full and self.status == EnrollmentStatus.ENROLLED:
            if not self.pk:  # New enrollment
                raise ValidationError('Event is at full capacity')

        # Check if event has already ended
        if self.event.is_past and self.status == EnrollmentStatus.ENROLLED:
            if not self.pk:  # New enrollment
                raise ValidationError('Cannot enroll in past events')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
