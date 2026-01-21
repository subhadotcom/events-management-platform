"""
Utility functions for the accounts app.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from .models import OTP


def send_otp_email(email, otp_code):
    """Send OTP to user's email"""
    subject = 'Verify Your Email - Events Platform'
    message = f"""
    Hello,
    
    Your OTP for email verification is: {otp_code}
    
    This OTP will expire in {settings.OTP_EXPIRY_MINUTES} minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    Events Platform Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def create_otp(email):
    """Create and send OTP for email verification"""
    # Invalidate all previous OTPs for this email
    OTP.objects.filter(email=email, is_used=False).update(is_used=True)
    
    # Generate new OTP
    otp_code = OTP.generate_otp()
    expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    
    otp = OTP.objects.create(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    
    # Send OTP email
    send_otp_email(email, otp_code)
    
    return otp


def verify_otp(email, otp_code):
    """Verify OTP for email"""
    try:
        otp = OTP.objects.filter(
            email=email,
            otp_code=otp_code,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp:
            return False, "Invalid OTP"
        
        # Increment attempts
        otp.attempts += 1
        otp.save()
        
        # Check if max attempts exceeded
        if otp.attempts > settings.OTP_MAX_ATTEMPTS:
            otp.is_used = True
            otp.save()
            return False, "Maximum verification attempts exceeded"
        
        # Check if expired
        if timezone.now() > otp.expires_at:
            otp.is_used = True
            otp.save()
            return False, "OTP has expired"
        
        # Valid OTP
        otp.is_used = True
        otp.save()
        return True, "Email verified successfully"
        
    except Exception as e:
        return False, str(e)


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses"""
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize error response format
        custom_response_data = {
            'detail': response.data.get('detail', str(exc)),
            'code': getattr(exc, 'default_code', 'error')
        }
        
        # Handle validation errors
        if isinstance(response.data, dict) and 'detail' not in response.data:
            errors = []
            for field, messages in response.data.items():
                if isinstance(messages, list):
                    errors.extend([f"{field}: {msg}" for msg in messages])
                else:
                    errors.append(f"{field}: {messages}")
            custom_response_data['detail'] = '; '.join(errors)
        
        response.data = custom_response_data
    
    return response
