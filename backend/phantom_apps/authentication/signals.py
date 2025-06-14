from django.db.models.signals import post_save, user_logged_in, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_out
from django.utils import timezone
from allauth.account.signals import email_confirmed
from .models import LoginAttempt, UserSession
from .utils import get_client_ip, parse_user_agent, get_user_location_from_ip
from .tasks import send_welcome_email

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Handle user creation"""
    if created:
        # Send welcome email for new users
        # Only send if email is not already verified (to avoid duplicate emails)
        if not instance.is_email_verified:
            try:
                send_welcome_email.delay(instance.id)
            except Exception as e:
                print(f"Failed to queue welcome email for {instance.email}: {e}")


@receiver(email_confirmed)
def email_confirmed_handler(sender, request, email_address, **kwargs):
    """Handle email confirmation from allauth"""
    user = email_address.user
    if not user.is_email_verified:
        user.is_email_verified = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=['is_email_verified', 'email_verified_at'])


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Handle successful user login"""
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        device_info = parse_user_agent(user_agent)
        location_info = get_user_location_from_ip(ip_address) if ip_address else {}
        
        # Create login attempt record
        LoginAttempt.objects.create(
            user=user,
            email_attempted=user.email,
            ip_address=ip_address or '127.0.0.1',
            user_agent=user_agent,
            success=True,
            country=location_info.get('country', ''),
            city=location_info.get('city', '')
        )
        
        # Update user's last login IP
        user.last_login_ip = ip_address
        user.save(update_fields=['last_login_ip'])
        
        # Create or update user session
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.update_or_create(
                user=user,
                session_key=session_key,
                defaults={
                    'ip_address': ip_address or '127.0.0.1',
                    'user_agent': user_agent,
                    'device_type': device_info['device_type'],
                    'browser': device_info['browser'],
                    'os': device_info['os'],
                    'is_active': True,
                }
            )


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """Handle failed user login"""
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        location_info = get_user_location_from_ip(ip_address) if ip_address else {}
        
        # Try to find the user by email or username
        username_or_email = credentials.get('username', '')
        user = None
        
        if username_or_email:
            try:
                if '@' in username_or_email:
                    user = User.objects.get(email=username_or_email.lower())
                else:
                    user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                pass
        
        # Create login attempt record
        LoginAttempt.objects.create(
            user=user,
            email_attempted=username_or_email,
            ip_address=ip_address or '127.0.0.1',
            user_agent=user_agent,
            success=False,
            failure_reason='Invalid credentials',
            country=location_info.get('country', ''),
            city=location_info.get('city', '')
        )
        
        # Increment failed login attempts for the user
        if user:
            user.increment_failed_login()


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """Handle user logout"""
    if request and user:
        session_key = request.session.session_key
        if session_key:
            # Deactivate user session
            UserSession.objects.filter(
                user=user,
                session_key=session_key
            ).update(is_active=False)

