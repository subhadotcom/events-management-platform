"""
Tests for events app.
"""

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserProfile, UserRole
from events.models import Event, Enrollment, EnrollmentStatus


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def seeker_user(db):
    user = User.objects.create_user(
        username='seeker@example.com',
        email='seeker@example.com',
        password='SecurePass123!'
    )
    UserProfile.objects.create(
        user=user,
        role=UserRole.SEEKER,
        email_verified=True
    )
    return user


@pytest.fixture
def facilitator_user(db):
    user = User.objects.create_user(
        username='facilitator@example.com',
        email='facilitator@example.com',
        password='SecurePass123!'
    )
    UserProfile.objects.create(
        user=user,
        role=UserRole.FACILITATOR,
        email_verified=True
    )
    return user


@pytest.fixture
def sample_event(facilitator_user):
    return Event.objects.create(
        title='Test Event',
        description='Test Description',
        language='English',
        location='Test Location',
        starts_at=timezone.now() + timedelta(days=7),
        ends_at=timezone.now() + timedelta(days=7, hours=2),
        capacity=10,
        created_by=facilitator_user
    )


@pytest.mark.django_db
class TestEventCreation:
    def test_facilitator_can_create_event(self, api_client, facilitator_user):
        """Test that facilitator can create events"""
        api_client.force_authenticate(user=facilitator_user)
        
        data = {
            'title': 'Django Workshop',
            'description': 'Learn Django',
            'language': 'English',
            'location': 'Mumbai',
            'starts_at': (timezone.now() + timedelta(days=10)).isoformat(),
            'ends_at': (timezone.now() + timedelta(days=10, hours=3)).isoformat(),
            'capacity': 20
        }
        
        response = api_client.post('/api/events/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Event.objects.filter(title='Django Workshop').exists()
    
    def test_seeker_cannot_create_event(self, api_client, seeker_user):
        """Test that seeker cannot create events"""
        api_client.force_authenticate(user=seeker_user)
        
        data = {
            'title': 'Django Workshop',
            'description': 'Learn Django',
            'language': 'English',
            'location': 'Mumbai',
            'starts_at': (timezone.now() + timedelta(days=10)).isoformat(),
            'ends_at': (timezone.now() + timedelta(days=10, hours=3)).isoformat(),
            'capacity': 20
        }
        
        response = api_client.post('/api/events/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEventSearch:
    def test_search_by_location(self, api_client, seeker_user, facilitator_user):
        """Test event search by location"""
        # Create test events
        Event.objects.create(
            title='Mumbai Event',
            description='Test',
            language='English',
            location='Mumbai',
            starts_at=timezone.now() + timedelta(days=5),
            ends_at=timezone.now() + timedelta(days=5, hours=2),
            created_by=facilitator_user
        )
        Event.objects.create(
            title='Delhi Event',
            description='Test',
            language='English',
            location='Delhi',
            starts_at=timezone.now() + timedelta(days=5),
            ends_at=timezone.now() + timedelta(days=5, hours=2),
            created_by=facilitator_user
        )
        
        api_client.force_authenticate(user=seeker_user)
        response = api_client.get('/api/events/search/?location=Mumbai')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['location'] == 'Mumbai'


@pytest.mark.django_db
class TestEnrollment:
    def test_seeker_can_enroll(self, api_client, seeker_user, sample_event):
        """Test that seeker can enroll in events"""
        api_client.force_authenticate(user=seeker_user)
        
        data = {'event_id': sample_event.id}
        response = api_client.post('/api/seeker/enroll', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Enrollment.objects.filter(
            event=sample_event,
            seeker=seeker_user
        ).exists()
    
    def test_cannot_enroll_twice(self, api_client, seeker_user, sample_event):
        """Test that seeker cannot enroll in same event twice"""
        api_client.force_authenticate(user=seeker_user)
        
        # First enrollment
        data = {'event_id': sample_event.id}
        api_client.post('/api/seeker/enroll', data, format='json')
        
        # Second enrollment
        response = api_client.post('/api/seeker/enroll', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_enroll_in_full_event(self, api_client, seeker_user, facilitator_user):
        """Test that enrollment fails when event is full"""
        # Create event with capacity of 1
        event = Event.objects.create(
            title='Small Event',
            description='Test',
            language='English',
            location='Mumbai',
            starts_at=timezone.now() + timedelta(days=5),
            ends_at=timezone.now() + timedelta(days=5, hours=2),
            capacity=1,
            created_by=facilitator_user
        )
        
        # Create another seeker and enroll them
        other_seeker = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='Pass123!'
        )
        UserProfile.objects.create(
            user=other_seeker,
            role=UserRole.SEEKER,
            email_verified=True
        )
        Enrollment.objects.create(
            event=event,
            seeker=other_seeker,
            status=EnrollmentStatus.ENROLLED
        )
        
        # Try to enroll current seeker
        api_client.force_authenticate(user=seeker_user)
        data = {'event_id': event.id}
        response = api_client.post('/api/seeker/enroll', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_facilitator_cannot_enroll(self, api_client, facilitator_user, sample_event):
        """Test that facilitator cannot enroll in events"""
        api_client.force_authenticate(user=facilitator_user)
        
        data = {'event_id': sample_event.id}
        response = api_client.post('/api/seeker/enroll', data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEnrollmentCancellation:
    def test_cancel_enrollment(self, api_client, seeker_user, sample_event):
        """Test enrollment cancellation"""
        # Create enrollment
        enrollment = Enrollment.objects.create(
            event=sample_event,
            seeker=seeker_user,
            status=EnrollmentStatus.ENROLLED
        )
        
        api_client.force_authenticate(user=seeker_user)
        response = api_client.post(f'/api/seeker/enrollments/{enrollment.id}/cancel')
        
        assert response.status_code == status.HTTP_200_OK
        enrollment.refresh_from_db()
        assert enrollment.status == EnrollmentStatus.CANCELED
