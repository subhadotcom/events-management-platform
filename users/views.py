from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .serializers import SignupSerializer, VerifyEmailSerializer
from .models import Profile

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Send OTP email
        otp = user.profile.otp
        print(f"Sending OTP {otp} to {user.email}") # For console backend
        send_mail(
            'Verify your email',
            f'Your OTP is {otp}',
            'noreply@events.com',
            [user.email],
            fail_silently=False,
        )

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(email=email)
            profile = user.profile
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if profile.is_verified:
            return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)
            
        if profile.otp != otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
        if profile.otp_expiry < timezone.now():
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
            
        profile.is_verified = True
        profile.otp = None
        profile.save()
        
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if not self.user.profile.is_verified:
            raise AuthenticationFailed("Email is not verified.")
            
        data['role'] = self.user.profile.role
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
