"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from .models import UserProfile, OTP


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'email_verified', 'created_at')
    list_filter = ('role', 'email_verified', 'created_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'attempts', 'is_used', 'expires_at', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email', 'otp_code')
    readonly_fields = ('created_at',)
