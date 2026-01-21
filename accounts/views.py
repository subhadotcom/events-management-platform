"""
Views for the accounts app.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import SignupSerializer, VerifyEmailSerializer, LoginSerializer, UserSerializer
from .utils import create_otp, verify_otp


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    User signup endpoint
    POST /auth/signup
    Body: {email, password, role}
    """
    serializer = SignupSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Generate and send OTP
            create_otp(user.email)
            
            return Response({
                'detail': f'User created successfully. OTP sent to {user.email}',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'detail': f'Error creating user: {str(e)}',
                'code': 'signup_error'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Return validation errors
    errors = []
    for field, messages in serializer.errors.items():
        if isinstance(messages, list):
            errors.extend([f"{field}: {msg}" for msg in messages])
        else:
            errors.append(f"{field}: {messages}")
    
    return Response({
        'detail': '; '.join(errors),
        'code': 'validation_error'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Email verification endpoint
    POST /auth/verify-email
    Body: {email, otp}
    """
    serializer = VerifyEmailSerializer(data=request.data)
    
    if not serializer.is_valid():
        errors = []
        for field, messages in serializer.errors.items():
            if isinstance(messages, list):
                errors.extend([f"{field}: {msg}" for msg in messages])
            else:
                errors.append(f"{field}: {messages}")
        
        return Response({
            'detail': '; '.join(errors),
            'code': 'validation_error'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp']
    
    # Verify OTP
    is_valid, message = verify_otp(email, otp_code)
    
    if is_valid:
        # Mark user as verified
        try:
            user = User.objects.get(email=email)
            user.profile.email_verified = True
            user.profile.save()
            
            return Response({
                'detail': 'Email verified successfully. You can now login.',
                'email': email
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'detail': 'User not found',
                'code': 'user_not_found'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({
            'detail': message,
            'code': 'otp_verification_failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login endpoint
    POST /auth/login
    Body: {email, password}
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        errors = []
        for field, messages in serializer.errors.items():
            if isinstance(messages, list):
                errors.extend([f"{field}: {msg}" for msg in messages])
            else:
                errors.append(f"{field}: {messages}")
        
        return Response({
            'detail': '; '.join(errors),
            'code': 'validation_error'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        user = User.objects.get(email=email)
        
        # Check if email is verified
        if not user.profile.email_verified:
            return Response({
                'detail': 'Email not verified. Please verify your email first.',
                'code': 'email_not_verified'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Authenticate user
        user = authenticate(username=email, password=password)
        
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Invalid credentials',
                'code': 'invalid_credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except User.DoesNotExist:
        return Response({
            'detail': 'Invalid credentials',
            'code': 'invalid_credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP endpoint
    POST /auth/resend-otp
    Body: {email}
    """
    email = request.data.get('email')
    
    if not email:
        return Response({
            'detail': 'Email is required',
            'code': 'email_required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        if user.profile.email_verified:
            return Response({
                'detail': 'Email already verified',
                'code': 'already_verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate and send new OTP
        create_otp(email)
        
        return Response({
            'detail': f'OTP sent to {email}',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'detail': 'User not found',
            'code': 'user_not_found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_current_user(request):
    """
    Get current authenticated user
    GET /auth/me
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
