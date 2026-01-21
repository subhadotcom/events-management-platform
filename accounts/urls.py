"""
URL configuration for accounts app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('signup', views.signup, name='signup'),
    path('verify-email', views.verify_email, name='verify-email'),
    path('login', views.login, name='login'),
    path('resend-otp', views.resend_otp, name='resend-otp'),
    path('refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('me', views.get_current_user, name='current-user'),
]
