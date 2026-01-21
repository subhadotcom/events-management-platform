"""
Serializers for the accounts app.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, UserRole


class SignupSerializer(serializers.Serializer):
    """Serializer for user signup"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=UserRole.choices, required=True)

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "detail": "A user with this email already exists.",
                "code": "email_exists"
            })
        return value.lower()

    def create(self, validated_data):
        """Create user and profile"""
        user = User.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.is_active = True  # User is active but not verified
        user.save()

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=validated_data['role'],
            email_verified=False
        )

        return user


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification"""
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6, min_length=6)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    role = serializers.CharField(source='profile.role', read_only=True)
    email_verified = serializers.BooleanField(source='profile.email_verified', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'email_verified', 'date_joined']
        read_only_fields = ['id', 'email', 'role', 'email_verified', 'date_joined']
