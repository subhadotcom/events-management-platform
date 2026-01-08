from rest_framework import serializers
from .models import Event, Enrollment

class EventSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    enrollment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'language', 'location',
            'starts_at', 'ends_at', 'capacity', 'available_seats',
            'enrollment_count', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'available_seats', 'enrollment_count']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class EnrollmentSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    starts_at = serializers.DateTimeField(source='event.starts_at', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'event', 'event_title', 'starts_at', 'status', 'created_at']
        read_only_fields = ['seeker', 'status', 'created_at']
