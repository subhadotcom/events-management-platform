from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from .models import Event, Enrollment
from .serializers import EventSerializer, EnrollmentSerializer
from .permissions import IsFacilitator, IsSeeker, IsEventOwner

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Event.objects.annotate(
            enrollment_count=Count('enrollments', filter=Q(enrollments__status='ENROLLED'))
        )
        
        # Search & Filter
        query = self.request.query_params.get('q')
        location = self.request.query_params.get('location')
        language = self.request.query_params.get('language')
        starts_after = self.request.query_params.get('starts_after')
        starts_before = self.request.query_params.get('starts_before')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if location:
            queryset = queryset.filter(location__icontains=location)
        if language:
            queryset = queryset.filter(language__iexact=language)
        if starts_after:
            queryset = queryset.filter(starts_at__gte=starts_after)
        if starts_before:
            queryset = queryset.filter(starts_at__lte=starts_before)

        return queryset.order_by('starts_at')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_events']:
            return [IsFacilitator(), IsEventOwner()] if self.action != 'create' and self.action != 'my_events' else [IsFacilitator()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def my_events(self, request):
        queryset = self.get_queryset().filter(created_by=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsSeeker])
    def enroll(self, request, pk=None):
        event = self.get_object()
        
        # Check capacity
        if event.capacity is not None and event.available_seats <= 0:
            return Response({"error": "Event is full"}, status=status.HTTP_400_BAD_REQUEST)

        # Check existing enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            event=event,
            seeker=request.user,
            defaults={'status': 'ENROLLED'}
        )

        if not created:
            if enrollment.status == 'CANCELED':
                enrollment.status = 'ENROLLED'
                enrollment.save()
            else:
                return Response({"error": "Already enrolled"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Enrolled successfully"}, status=status.HTTP_201_CREATED)

class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsSeeker]

    def get_queryset(self):
        return Enrollment.objects.filter(seeker=self.request.user)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        queryset = self.get_queryset().filter(
            event__starts_at__gte=timezone.now(),
            status='ENROLLED'
        ).order_by('event__starts_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        queryset = self.get_queryset().filter(
            event__ends_at__lt=timezone.now(),
            status='ENROLLED'
        ).order_by('-event__ends_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
