"""
Views for the events app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from accounts.permissions import IsSeekerUser, IsFacilitatorUser
from .models import Event, Enrollment, EnrollmentStatus
from .serializers import (
    EventSerializer, EventListSerializer, EnrollmentSerializer,
    EnrollmentCreateSerializer, FacilitatorEventSerializer
)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for Event CRUD operations"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter events based on search parameters"""
        queryset = Event.objects.all()
        
        # Search filters
        location = self.request.query_params.get('location', None)
        language = self.request.query_params.get('language', None)
        starts_after = self.request.query_params.get('starts_after', None)
        starts_before = self.request.query_params.get('starts_before', None)
        q = self.request.query_params.get('q', None)
        
        # Filter by location
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by language
        if language:
            queryset = queryset.filter(language__icontains=language)
        
        # Filter by start date range
        if starts_after:
            queryset = queryset.filter(starts_at__gte=starts_after)
        
        if starts_before:
            queryset = queryset.filter(starts_at__lte=starts_before)
        
        # Search in title and description
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )
        
        # Default ordering - upcoming events first
        queryset = queryset.order_by('starts_at')
        
        return queryset

    def get_serializer_class(self):
        """Use different serializers for list and detail"""
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsFacilitatorUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Set the creator as current user"""
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        """Only allow creator to update"""
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response({
                'detail': 'You do not have permission to edit this event',
                'code': 'permission_denied'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only allow creator to delete"""
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response({
                'detail': 'You do not have permission to delete this event',
                'code': 'permission_denied'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsFacilitatorUser])
def my_events(request):
    """
    List facilitator's own events with enrollment counts
    GET /api/facilitator/events
    """
    events = Event.objects.filter(created_by=request.user).order_by('-created_at')
    serializer = FacilitatorEventSerializer(events, many=True)
    
    return Response({
        'count': events.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSeekerUser])
def enroll_event(request):
    """
    Enroll in an event
    POST /api/seeker/enroll
    Body: {event_id}
    """
    serializer = EnrollmentCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        errors = []
        for field, messages in serializer.errors.items():
            if isinstance(messages, list):
                for msg in messages:
                    if isinstance(msg, dict):
                        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
                    errors.append(f"{field}: {msg}")
            else:
                errors.append(f"{field}: {messages}")
        
        return Response({
            'detail': '; '.join(errors),
            'code': 'validation_error'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    event_id = serializer.validated_data['event_id']
    
    try:
        event = Event.objects.get(id=event_id)
        
        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(
            event=event,
            seeker=request.user,
            status=EnrollmentStatus.ENROLLED
        ).first()
        
        if existing_enrollment:
            return Response({
                'detail': 'Already enrolled in this event',
                'code': 'already_enrolled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            event=event,
            seeker=request.user,
            status=EnrollmentStatus.ENROLLED
        )
        
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )
        
    except Event.DoesNotExist:
        return Response({
            'detail': 'Event not found',
            'code': 'event_not_found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'detail': str(e),
            'code': 'enrollment_error'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSeekerUser])
def cancel_enrollment(request, enrollment_id):
    """
    Cancel an enrollment
    POST /api/seeker/enrollments/{id}/cancel
    """
    try:
        enrollment = Enrollment.objects.get(
            id=enrollment_id,
            seeker=request.user
        )
        
        if enrollment.status == EnrollmentStatus.CANCELED:
            return Response({
                'detail': 'Enrollment already canceled',
                'code': 'already_canceled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment.status = EnrollmentStatus.CANCELED
        enrollment.save()
        
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_200_OK
        )
        
    except Enrollment.DoesNotExist:
        return Response({
            'detail': 'Enrollment not found',
            'code': 'enrollment_not_found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeekerUser])
def my_enrollments(request):
    """
    List seeker's enrollments
    GET /api/seeker/enrollments?type=upcoming|past
    """
    enrollment_type = request.query_params.get('type', 'all')
    
    enrollments = Enrollment.objects.filter(
        seeker=request.user,
        status=EnrollmentStatus.ENROLLED
    ).select_related('event')
    
    # Filter by type
    if enrollment_type == 'upcoming':
        enrollments = enrollments.filter(event__starts_at__gt=timezone.now())
    elif enrollment_type == 'past':
        enrollments = enrollments.filter(event__ends_at__lt=timezone.now())
    
    enrollments = enrollments.order_by('-created_at')
    
    serializer = EnrollmentSerializer(enrollments, many=True)
    
    return Response({
        'count': enrollments.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_events(request):
    """
    Search events with filters
    GET /api/events/search?location=&language=&starts_after=&starts_before=&q=
    """
    queryset = Event.objects.all()
    
    # Search filters
    location = request.query_params.get('location')
    language = request.query_params.get('language')
    starts_after = request.query_params.get('starts_after')
    starts_before = request.query_params.get('starts_before')
    q = request.query_params.get('q')
    
    # Apply filters
    if location:
        queryset = queryset.filter(location__icontains=location)
    
    if language:
        queryset = queryset.filter(language__icontains=language)
    
    if starts_after:
        queryset = queryset.filter(starts_at__gte=starts_after)
    
    if starts_before:
        queryset = queryset.filter(starts_at__lte=starts_before)
    
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )
    
    # Default filter - only upcoming events
    queryset = queryset.filter(starts_at__gte=timezone.now())
    
    # Order by start date (upcoming first)
    queryset = queryset.order_by('starts_at')
    
    # Pagination
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    serializer = EventListSerializer(page, many=True)
    
    return paginator.get_paginated_response(serializer.data)
