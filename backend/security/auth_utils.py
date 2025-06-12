import os
import secrets
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from .models import CustomUser, EmailVerification, PasswordReset
from django.db import models
from django.core.cache import cache

def generate_token():
    return secrets.token_urlsafe(32)

def send_verification_email(user):
    """Send email verification link to user"""
    token = generate_token()
    expiry = timezone.now() + timedelta(hours=24)
    
    # Create verification record
    verification = EmailVerification.objects.create(
        user=user,
        token=token,
        expires_at=expiry
    )
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    context = {
        'user': user,
        'verification_url': verification_url,
        'expiry_hours': 24
    }
    
    html_message = render_to_string('security/email/verify_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Verify Your Email Address',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )
    
    return verification

def verify_email(token):
    """Verify user's email using token"""
    try:
        verification = EmailVerification.objects.get(
            token=token,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        
        user = verification.user
        user.email_verified = True
        user.verification_status = 'verified'
        user.save()
        
        verification.is_used = True
        verification.used_at = timezone.now()
        verification.save()
        
        return True, user
    except EmailVerification.DoesNotExist:
        return False, None

def send_password_reset_email(user, request=None):
    """Send password reset email to user"""
    token = generate_token()
    expiry = timezone.now() + timedelta(hours=1)
    
    # Create password reset record
    reset = PasswordReset.objects.create(
        user=user,
        token=token,
        expires_at=expiry,
        ip_address=request.META.get('REMOTE_ADDR') if request else None
    )
    
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
    
    context = {
        'user': user,
        'reset_url': reset_url,
        'expiry_minutes': 60
    }
    
    html_message = render_to_string('security/email/reset_password.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Reset Your Password',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )
    
    return reset

def verify_password_reset_token(token):
    """Verify password reset token"""
    try:
        reset = PasswordReset.objects.get(
            token=token,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        return True, reset.user
    except PasswordReset.DoesNotExist:
        return False, None

def reset_password(token, new_password):
    """Reset user's password using token"""
    valid, user = verify_password_reset_token(token)
    if not valid or not user:
        return False
    
    try:
        reset = PasswordReset.objects.get(token=token)
        user.set_password(new_password)
        user.save()
        
        reset.is_used = True
        reset.used_at = timezone.now()
        reset.save()
        
        return True
    except PasswordReset.DoesNotExist:
        return False

def create_merchant_user(business_name, registration_number, contact_email, 
                        contact_phone, admin_name, admin_email, password):
    """Create a new merchant user with associated merchant profile"""
    from .models import MerchantUser
    
    # Create the user first
    user = CustomUser.objects.create_user(
        username=f"merchant_{registration_number}",
        email=admin_email,
        password=password,
        role='merchant'
    )
    
    # Create the merchant profile
    merchant_profile = MerchantUser.objects.create(
        user=user,
        business_name=business_name,
        registration_number=registration_number,
        contact_email=contact_email,
        contact_phone=contact_phone,
        business_type='standard',
        address=''
    )
    
    # Send verification email
    send_verification_email(user)
    
    return user, merchant_profile

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

def send_otp_email(user, otp):
    """Send OTP via email using Google SMTP"""
    context = {
        'user': user,
        'otp': otp,
        'expiry_minutes': 5
    }
    
    html_message = render_to_string('security/email/otp_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Your Login OTP',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )

def validate_login(username_or_email, password):
    """
    Validate user login credentials and handle 2FA
    
    For merchants: Use admin_email as username_or_email
    For customers: Use username or email as username_or_email
    For system admins: Use username or email as username_or_email
    """
    try:
        # Try to get user by username or email
        user = CustomUser.objects.get(
            models.Q(username=username_or_email) | 
            models.Q(email=username_or_email)
        )
        
        # Check if account is locked
        if user.is_account_locked():
            return False, "Account is temporarily locked. Please try again later."
        
        # Check password
        if not user.check_password(password):
            user.increment_failed_login()
            return False, "Invalid credentials."
        
        # Reset failed login attempts on successful login
        user.reset_failed_login()
        
        # Generate and send OTP
        otp = generate_otp()
        # Store OTP in cache with 5-minute expiry
        cache_key = f"login_otp_{user.id}"
        cache.set(cache_key, otp, timeout=300)  # 5 minutes
        
        # Send OTP via email
        send_otp_email(user, otp)
        
        # Return user object with a message indicating OTP was sent
        return True, {"user": user, "message": "OTP sent to your email. Please verify to complete login."}
        
    except CustomUser.DoesNotExist:
        return False, "Invalid credentials."

def verify_login_otp(user_id, otp):
    """Verify the OTP provided during login"""
    cache_key = f"login_otp_{user_id}"
    stored_otp = cache.get(cache_key)
    
    if not stored_otp:
        return False, "OTP has expired. Please request a new one."
    
    if otp != stored_otp:
        return False, "Invalid OTP. Please try again."
    
    # Clear the OTP from cache
    cache.delete(cache_key)
    return True, "OTP verified successfully."