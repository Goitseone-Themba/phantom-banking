from celery import shared_task
from django.contrib.auth import get_user_model
from .utils import (
    send_verification_email_sync,
    send_password_reset_email_sync,
    send_welcome_email_sync,
    cleanup_expired_tokens
)

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_verification_email(self, user_id):
    """Send email verification email asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        success = send_verification_email_sync(user)
        if not success:
            raise Exception("Failed to send verification email")
        return f"Verification email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with ID {user_id} not found"
    except Exception as exc:
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        return f"Failed to send verification email after {self.max_retries} attempts: {str(exc)}"


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, ip_address=None):
    """Send password reset email asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        success = send_password_reset_email_sync(user, ip_address)
        if not success:
            raise Exception("Failed to send password reset email")
        return f"Password reset email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with ID {user_id} not found"
    except Exception as exc:
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        return f"Failed to send password reset email after {self.max_retries} attempts: {str(exc)}"


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """Send welcome email asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        success = send_welcome_email_sync(user)
        if not success:
            raise Exception("Failed to send welcome email")
        return f"Welcome email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with ID {user_id} not found"
    except Exception as exc:
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        return f"Failed to send welcome email after {self.max_retries} attempts: {str(exc)}"


@shared_task
def cleanup_expired_tokens_task():
    """Clean up expired tokens periodically"""
    result = cleanup_expired_tokens()
    return f"Cleaned up {result['email_tokens_deleted']} email tokens and {result['reset_tokens_deleted']} reset tokens"


@shared_task
def send_bulk_notification(user_ids, subject, message, html_message=None):
    """Send bulk notification emails"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    users = User.objects.filter(id__in=user_ids, is_active=True)
    sent_count = 0
    failed_count = 0
    
    for user in users:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phantombanking.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send notification to {user.email}: {e}")
            failed_count += 1
    
    return f"Sent {sent_count} notifications, {failed_count} failed"

