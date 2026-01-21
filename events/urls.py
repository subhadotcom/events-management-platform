"""
URL configuration for events app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    # Event search
    path('events/search/', views.search_events, name='event-search'),

    # Event CRUD (REST)
    path('', include(router.urls)),
    
    # Seeker endpoints
    path('seeker/enroll', views.enroll_event, name='seeker-enroll'),
    path('seeker/enrollments', views.my_enrollments, name='seeker-enrollments'),
    path('seeker/enrollments/<int:enrollment_id>/cancel', views.cancel_enrollment, name='cancel-enrollment'),
    
    # Facilitator endpoints
    path('facilitator/events', views.my_events, name='facilitator-events'),
]
