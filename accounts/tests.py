"""
Tests for accounts app.
"""

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserProfile, OTP, UserRole
from accounts.utils import create_otp, verify_otp


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(email, password, role, verified=False):
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        UserProfile.objects.create(
            user=user,
            role=role,
            email_verified=verified
        )
        return user
    return make_user


@pytest.mark.django_db
class TestSignup:
    def test_signup_seeker_success(self, api_client):
        """Test successful seeker signup"""
        data = {
            'email': 'testseeker@example.com',
            'password': 'SecurePass123!',
            'role': 'Seeker'
        }
        response = api_client.post('/auth/signup', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'detail' in response.data
        assert 'email' in response.data
        
        # Verify user created
        user = User.objects.get(email=data['email'])
        assert user.profile.role == UserRole.SEEKER
        assert not user.profile.email_verified
    
    def test_signup_facilitator_success(self, api_client):
        """Test successful facilitator signup"""
        data = {
            'email': 'testfacilitator@example.com',
            'password': 'SecurePass123!',
            'role': 'Facilitator'
        }
        response = api_client.post('/auth/signup', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email=data['email'])
        assert user.profile.role == UserRole.FACILITATOR
    
    def test_signup_duplicate_email(self, api_client, create_user):
        """Test signup with duplicate email"""
        create_user('existing@example.com', 'Pass123!', UserRole.SEEKER)
        
        data = {
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'role': 'Seeker'
        }
        response = api_client.post('/auth/signup', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_signup_invalid_role(self, api_client):
        """Test signup with invalid role"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'role': 'InvalidRole'
        }
        response = api_client.post('/auth/signup', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestEmailVerification:
    def test_verify_email_success(self, api_client, create_user):
        """Test successful email verification"""
        user = create_user('test@example.com', 'Pass123!', UserRole.SEEKER, verified=False)
        otp = create_otp(user.email)
        
        data = {
            'email': user.email,
            'otp': otp.otp_code
        }
        response = api_client.post('/auth/verify-email', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.profile.email_verified
    
    def test_verify_email_invalid_otp(self, api_client, create_user):
        """Test verification with invalid OTP"""
        user = create_user('test@example.com', 'Pass123!', UserRole.SEEKER, verified=False)
        create_otp(user.email)
        
        data = {
            'email': user.email,
            'otp': '999999'
        }
        response = api_client.post('/auth/verify-email', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_verify_email_expired_otp(self, api_client, create_user):
        """Test verification with expired OTP"""
        user = create_user('test@example.com', 'Pass123!', UserRole.SEEKER, verified=False)
        otp = OTP.objects.create(
            email=user.email,
            otp_code='123456',
            expires_at=timezone.now() - timedelta(minutes=10)
        )
        
        data = {
            'email': user.email,
            'otp': otp.otp_code
        }
        response = api_client.post('/auth/verify-email', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, create_user):
        """Test successful login"""
        user = create_user('test@example.com', 'SecurePass123!', UserRole.SEEKER, verified=True)
        
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        response = api_client.post('/auth/login', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_unverified_email(self, api_client, create_user):
        """Test login with unverified email"""
        user = create_user('test@example.com', 'SecurePass123!', UserRole.SEEKER, verified=False)
        
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        response = api_client.post('/auth/login', data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_login_invalid_credentials(self, api_client, create_user):
        """Test login with wrong password"""
        user = create_user('test@example.com', 'SecurePass123!', UserRole.SEEKER, verified=True)
        
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        response = api_client.post('/auth/login', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
