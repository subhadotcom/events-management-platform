"""
Admin configuration for events app.
"""

from django.contrib import admin
from .models import Event, Enrollment


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'location', 'starts_at', 'ends_at', 'capacity', 'created_by', 'created_at')
    list_filter = ('language', 'location', 'starts_at', 'created_at')
    search_fields = ('title', 'description', 'location', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'starts_at'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('seeker', 'event', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('seeker__email', 'event__title')
    readonly_fields = ('created_at', 'updated_at')
