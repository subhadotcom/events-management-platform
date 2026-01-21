"""
Models for the accounts app.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import random
import string


class UserRole(models.TextChoices):
    """User role choices"""
    SEEKER = 'Seeker', 'Seeker'
    FACILITATOR = 'Facilitator', 'Facilitator'


class UserProfile(models.Model):
    """Extended user profile with role and verification status"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=UserRole.choices)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email_verified']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class OTP(models.Model):
    """One-time password for email verification"""
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otps'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['email', 'otp_code']),
        ]

    def __str__(self):
        return f"{self.email} - {self.otp_code}"

    def is_valid(self):
        """Check if OTP is still valid"""
        return (
            not self.is_used and
            self.attempts < 3 and
            timezone.now() < self.expires_at
        )

    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
