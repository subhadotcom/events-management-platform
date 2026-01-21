"""
Serializers for the events app.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Event, Enrollment, EnrollmentStatus


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    total_enrollments = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'language', 'location',
            'starts_at', 'ends_at', 'capacity', 'created_by', 'created_by_email',
            'total_enrollments', 'available_seats', 'is_past', 'is_upcoming',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate event dates"""
        starts_at = data.get('starts_at')
        ends_at = data.get('ends_at')

        if starts_at and ends_at:
            if ends_at <= starts_at:
                raise serializers.ValidationError({
                    "detail": "End time must be after start time",
                    "code": "invalid_dates"
                })

        # For creation, check if start time is in the past
        if not self.instance and starts_at:
            if starts_at < timezone.now():
                raise serializers.ValidationError({
                    "detail": "Cannot create events in the past",
                    "code": "past_event"
                })

        return data


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event listings"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    total_enrollments = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'language', 'location', 'starts_at', 'ends_at',
            'capacity', 'created_by_email', 'total_enrollments', 'available_seats'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_details = EventListSerializer(source='event', read_only=True)
    seeker_email = serializers.EmailField(source='seeker.email', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'event', 'event_title', 'event_details', 'seeker',
            'seeker_email', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'seeker', 'created_at', 'updated_at']

    def validate_event(self, value):
        """Validate event enrollment"""
        # Check if event exists and is not past
        if value.is_past:
            raise serializers.ValidationError({
                "detail": "Cannot enroll in past events",
                "code": "past_event"
            })

        # Check capacity
        if value.is_full:
            raise serializers.ValidationError({
                "detail": "Event is at full capacity",
                "code": "event_full"
            })

        return value


class EnrollmentCreateSerializer(serializers.Serializer):
    """Serializer for creating enrollment"""
    event_id = serializers.IntegerField(required=True)

    def validate_event_id(self, value):
        """Validate event exists"""
        try:
            event = Event.objects.get(id=value)
            
            # Check if event is past
            if event.is_past:
                raise serializers.ValidationError({
                    "detail": "Cannot enroll in past events",
                    "code": "past_event"
                })
            
            # Check capacity
            if event.is_full:
                raise serializers.ValidationError({
                    "detail": "Event is at full capacity",
                    "code": "event_full"
                })
            
            return value
            
        except Event.DoesNotExist:
            raise serializers.ValidationError({
                "detail": "Event not found",
                "code": "event_not_found"
            })


class FacilitatorEventSerializer(serializers.ModelSerializer):
    """Serializer for facilitator's event list with enrollment stats"""
    total_enrollments = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'language', 'location',
            'starts_at', 'ends_at', 'capacity', 'total_enrollments',
            'available_seats', 'created_at', 'updated_at'
        ]
