from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    language = models.CharField(max_length=50, db_index=True)
    location = models.CharField(max_length=255, db_index=True)
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def available_seats(self):
        if self.capacity is None:
            return None
        enrolled_count = self.enrollments.filter(status='ENROLLED').count()
        return max(0, self.capacity - enrolled_count)

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('ENROLLED', 'Enrolled'),
        ('CANCELED', 'Canceled'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='enrollments')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'seeker')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seeker.email} -> {self.event.title}"
