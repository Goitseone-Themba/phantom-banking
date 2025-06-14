import secrets
import string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def get_client_ip(request):
    """Get client IP address from request"""
    if not request:
        return None
        
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_verification_token(length=32):
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_email_verification_token(user):
    """Create email verification token for user"""
    from .models import EmailVerificationToken
    
    # Invalidate any existing tokens for this user
    EmailVerificationToken.objects.filter(
        user=user, 
        email=user.email,
        used_at__isnull=True
    ).update(used_at=timezone.now())
    
    # Create new token
    token = generate_verification_token()
    expires_at = timezone.now() + timedelta(hours=24)  # 24 hour expiry
    
    verification_token = EmailVerificationToken.objects.create(
        user=user,
        token=token,
        email=user.email,
        expires_at=expires_at
    )
    
    return verification_token


def create_password_reset_token(user, ip_address=None):
    """Create password reset token for user"""
    from .models import PasswordResetToken
    
    # Invalidate any existing tokens for this user
    PasswordResetToken.objects.filter(
        user=user,
        used_at__isnull=True
    ).update(used_at=timezone.now())
    
    # Create new token
    token = generate_verification_token()
    expires_at = timezone.now() + timedelta(hours=1)  # 1 hour expiry
    
    reset_token = PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at,
        ip_address=ip_address
    )
    
    return reset_token


def send_verification_email_sync(user):
    """Send email verification email synchronously"""
    verification_token = create_email_verification_token(user)
    
    # Build verification URL
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    verification_url = f"{frontend_url}/auth/verify-email?token={verification_token.token}"
    
    # Email context
    context = {
        'user': user,
        'verification_url': verification_url,
        'token': verification_token.token,
        'site_name': 'Phantom Banking',
        'expires_hours': 24,
    }
    
    # Render email templates
    subject = f"Verify your email address - Phantom Banking"
    html_message = render_to_string('authentication/emails/verify_email.html', context)
    plain_message = render_to_string('authentication/emails/verify_email.txt', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phantombanking.com'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send verification email to {user.email}: {e}")
        return False


def send_password_reset_email_sync(user, ip_address=None):
    """Send password reset email synchronously"""
    reset_token = create_password_reset_token(user, ip_address)
    
    # Build reset URL
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    reset_url = f"{frontend_url}/auth/reset-password?token={reset_token.token}"
    
    # Email context
    context = {
        'user': user,
        'reset_url': reset_url,
        'token': reset_token.token,
        'site_name': 'Phantom Banking',
        'expires_hours': 1,
        'ip_address': ip_address,
    }
    
    # Render email templates
    subject = f"Reset your password - Phantom Banking"
    html_message = render_to_string('authentication/emails/password_reset.html', context)
    plain_message = render_to_string('authentication/emails/password_reset.txt', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phantombanking.com'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send password reset email to {user.email}: {e}")
        return False


def send_welcome_email_sync(user):
    """Send welcome email after successful registration"""
    # Email context
    context = {
        'user': user,
        'site_name': 'Phantom Banking',
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
    }
    
    # Render email templates
    subject = f"Welcome to Phantom Banking, {user.first_name}!"
    html_message = render_to_string('authentication/emails/welcome.html', context)
    plain_message = render_to_string('authentication/emails/welcome.txt', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phantombanking.com'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send welcome email to {user.email}: {e}")
        return False


def parse_user_agent(user_agent):
    """Parse user agent string to extract device info"""
    if not user_agent:
        return {'device_type': '', 'browser': '', 'os': ''}
    
    user_agent = user_agent.lower()
    
    # Detect device type
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        device_type = 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    
    # Detect browser
    if 'chrome' in user_agent:
        browser = 'Chrome'
    elif 'firefox' in user_agent:
        browser = 'Firefox'
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        browser = 'Safari'
    elif 'edge' in user_agent:
        browser = 'Edge'
    elif 'opera' in user_agent:
        browser = 'Opera'
    else:
        browser = 'Unknown'
    
    # Detect OS
    if 'windows' in user_agent:
        os = 'Windows'
    elif 'mac' in user_agent:
        os = 'macOS'
    elif 'linux' in user_agent:
        os = 'Linux'
    elif 'android' in user_agent:
        os = 'Android'
    elif 'ios' in user_agent or 'iphone' in user_agent or 'ipad' in user_agent:
        os = 'iOS'
    else:
        os = 'Unknown'
    
    return {
        'device_type': device_type,
        'browser': browser,
        'os': os
    }


def validate_password_strength(password):
    """Validate password strength beyond Django's default validators"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit.")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;':,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain at least one special character.")
    
    return errors


def cleanup_expired_tokens():
    """Clean up expired verification and reset tokens"""
    from .models import EmailVerificationToken, PasswordResetToken
    
    now = timezone.now()
    
    # Delete expired email verification tokens
    expired_email_tokens = EmailVerificationToken.objects.filter(expires_at__lt=now)
    email_count = expired_email_tokens.count()
    expired_email_tokens.delete()
    
    # Delete expired password reset tokens
    expired_reset_tokens = PasswordResetToken.objects.filter(expires_at__lt=now)
    reset_count = expired_reset_tokens.count()
    expired_reset_tokens.delete()
    
    return {
        'email_tokens_deleted': email_count,
        'reset_tokens_deleted': reset_count
    }


def get_user_location_from_ip(ip_address):
    """Get approximate location from IP address (stub implementation)"""
    # This is a stub implementation
    # In production, you might want to use a service like GeoIP2 or IPStack
    return {
        'country': 'Unknown',
        'city': 'Unknown'
    }

