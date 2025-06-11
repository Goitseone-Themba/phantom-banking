# backend/phantom_apps/kyc/tasks.py

from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging
from datetime import timedelta

from .models import KYCRecord, KYCEvent
from .services.veriff_service import VeriffService
from .services.wallet_service import WalletService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def check_kyc_status_periodic(self):
    """
    Periodic task to check KYC status for pending verifications
    """
    try:
        # Get records that need status update
        pending_records = KYCRecord.objects.filter(
            status__in=[KYCRecord.Status.PENDING, KYCRecord.Status.IN_PROGRESS],
            veriff_session_id__isnull=False,
            updated_at__lt=timezone.now() - timedelta(minutes=5)  # Don't check too frequently
        )
        
        veriff_service = VeriffService()
        updated_count = 0
        
        for kyc_record in pending_records:
            try:
                success, result = veriff_service.get_session_status(kyc_record.veriff_session_id)
                
                if success:
                    verification = result.get('verification', {})
                    decision = verification.get('decision')
                    
                    if decision and decision != kyc_record.veriff_decision:
                        kyc_record.veriff_decision = decision
                        kyc_record.veriff_code = verification.get('code')
                        kyc_record.veriff_reason = verification.get('reason')
                        
                        if decision == 'approved':
                            kyc_record.approve()
                            # Send approval notification
                            send_kyc_approval_notification.delay(kyc_record.user.id)
                            updated_count += 1
                            
                        elif decision == 'declined':
                            kyc_record.reject(reason=verification.get('reason'))
                            # Send rejection notification
                            send_kyc_rejection_notification.delay(kyc_record.user.id, verification.get('reason'))
                            updated_count += 1
                            
                        else:
                            kyc_record.status = KYCRecord.Status.RESUBMISSION_REQUESTED
                            kyc_record.save()
                            # Send resubmission notification
                            send_kyc_resubmission_notification.delay(kyc_record.user.id, verification.get('reason'))
                            updated_count += 1
                
            except Exception as e:
                logger.error(f"Error checking KYC status for record {kyc_record.id}: {str(e)}")
                continue
        
        logger.info(f"KYC status check completed. Updated {updated_count} records.")
        return f"Updated {updated_count} KYC records"
        
    except Exception as exc:
        logger.error(f"Error in check_kyc_status_periodic: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_kyc_approval_notification(self, user_id):
    """
    Send notification when KYC is approved
    """
    try:
        user = User.objects.get(id=user_id)
        kyc_record = user.kyc_record
        
        # Send email notification
        subject = 'KYC Verification Approved - Phantom Banking'
        
        html_message = render_to_string('kyc/emails/approval.html', {
            'user': user,
            'kyc_record': kyc_record,
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
        })
        
        text_message = render_to_string('kyc/emails/approval.txt', {
            'user': user,
            'kyc_record': kyc_record,
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
        })
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        # Create in-app notification
        create_in_app_notification.delay(
            user_id=user_id,
            title='KYC Verification Approved',
            message='Your identity verification has been successfully completed. Your wallet has been upgraded with higher limits.',
            notification_type='KYC_APPROVED'
        )
        
        # Trigger wallet upgrade
        upgrade_wallet_after_kyc.delay(user_id)
        
        logger.info(f"Sent KYC approval notification to user {user_id}")
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for KYC approval notification")
    except Exception as exc:
        logger.error(f"Error sending KYC approval notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_kyc_rejection_notification(self, user_id, reason=None):
    """
    Send notification when KYC is rejected
    """
    try:
        user = User.objects.get(id=user_id)
        kyc_record = user.kyc_record
        
        subject = 'KYC Verification Update - Phantom Banking'
        
        html_message = render_to_string('kyc/emails/rejection.html', {
            'user': user,
            'kyc_record': kyc_record,
            'reason': reason,
            'support_url': f"{settings.FRONTEND_URL}/support",
            'retry_url': f"{settings.FRONTEND_URL}/kyc"
        })
        
        text_message = render_to_string('kyc/emails/rejection.txt', {
            'user': user,
            'kyc_record': kyc_record,
            'reason': reason,
            'support_url': f"{settings.FRONTEND_URL}/support",
            'retry_url': f"{settings.FRONTEND_URL}/kyc"
        })
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        # Create in-app notification
        create_in_app_notification.delay(
            user_id=user_id,
            title='KYC Verification Update',
            message=f'Your verification could not be completed. {reason or "Please contact support for assistance."}',
            notification_type='KYC_REJECTED'
        )
        
        logger.info(f"Sent KYC rejection notification to user {user_id}")
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for KYC rejection notification")
    except Exception as exc:
        logger.error(f"Error sending KYC rejection notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_kyc_resubmission_notification(self, user_id, reason=None):
    """
    Send notification when KYC requires resubmission
    """
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'KYC Verification - Additional Information Required'
        
        html_message = render_to_string('kyc/emails/resubmission.html', {
            'user': user,
            'reason': reason,
            'retry_url': f"{settings.FRONTEND_URL}/kyc"
        })
        
        text_message = render_to_string('kyc/emails/resubmission.txt', {
            'user': user,
            'reason': reason,
            'retry_url': f"{settings.FRONTEND_URL}/kyc"
        })
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        # Create in-app notification
        create_in_app_notification.delay(
            user_id=user_id,
            title='KYC Verification - Action Required',
            message=f'Please resubmit your verification documents. {reason or ""}',
            notification_type='KYC_RESUBMISSION'
        )
        
        logger.info(f"Sent KYC resubmission notification to user {user_id}")
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for KYC resubmission notification")
    except Exception as exc:
        logger.error(f"Error sending KYC resubmission notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def upgrade_wallet_after_kyc(self, user_id):
    """
    Upgrade user's wallet after successful KYC verification
    """
    try:
        user = User.objects.get(id=user_id)
        wallet_service = WalletService()
        
        success, result = wallet_service.upgrade_wallet_after_kyc(user)
        
        if success:
            logger.info(f"Successfully upgraded wallet for user {user_id}")
            
            # Send wallet upgrade notification
            create_in_app_notification.delay(
                user_id=user_id,
                title='Wallet Upgraded!',
                message='Your wallet has been upgraded with higher transaction limits and premium features.',
                notification_type='WALLET_UPGRADED'
            )
        else:
            logger.error(f"Failed to upgrade wallet for user {user_id}: {result}")
            
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for wallet upgrade")
    except Exception as exc:
        logger.error(f"Error upgrading wallet: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def create_in_app_notification(self, user_id, title, message, notification_type):
    """
    Create an in-app notification
    """
    try:
        # This assumes you have a Notification model - adjust import as needed
        from ...notifications.models import Notification
        
        user = User.objects.get(id=user_id)
        
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            is_read=False
        )
        
        logger.info(f"Created in-app notification for user {user_id}")
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for notification")
    except Exception as exc:
        logger.warning(f"Could not create in-app notification: {str(exc)}")
        # Don't retry for notification failures


@shared_task
def cleanup_expired_kyc_sessions():
    """
    Clean up KYC sessions that have been pending for too long
    """
    try:
        # Find records that have been pending for more than 24 hours
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        expired_records = KYCRecord.objects.filter(
            status=KYCRecord.Status.PENDING,
            created_at__lt=cutoff_time,
            veriff_session_id__isnull=False
        )
        
        count = 0
        for record in expired_records:
            # Mark as expired and create event
            record.status = KYCRecord.Status.REJECTED
            record.admin_notes = "Session expired - no user action within 24 hours"
            record.save()
            
            KYCEvent.objects.create(
                kyc_record=record,
                event_type=KYCEvent.EventType.EXPIRED,
                description="KYC session expired due to inactivity",
                metadata={"auto_expired": True, "hours_elapsed": 24}
            )
            
            # Send expiration notification
            send_kyc_expiration_notification.delay(record.user.id)
            count += 1
        
        logger.info(f"Cleaned up {count} expired KYC sessions")
        return f"Cleaned up {count} expired sessions"
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_kyc_sessions: {str(e)}")
        raise


@shared_task(bind=True, max_retries=3)
def send_kyc_expiration_notification(self, user_id):
    """
    Send notification when KYC session expires
    """
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'KYC Verification Session Expired - Phantom Banking'
        
        html_message = render_to_string('kyc/emails/expiration.html', {
            'user': user,
            'retry_url': f"{settings.FRONTEND_URL}/kyc"
        })
        
        text_message = render_to_string('kyc/emails/expiration.txt', {
            'user': user,
            'retry_url': f"{settings.FRONTEND_URL}/kyc"
        })
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        logger.info(f"Sent KYC expiration notification to user {user_id}")
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for expiration notification")
    except Exception as exc:
        logger.error(f"Error sending expiration notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task
def generate_kyc_report():
    """
    Generate daily KYC statistics report
    """
    try:
        from django.db.models import Count
        from datetime import date
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Get statistics
        total_records = KYCRecord.objects.count()
        daily_records = KYCRecord.objects.filter(created_at__date=yesterday).count()
        
        status_breakdown = KYCRecord.objects.values('status').annotate(count=Count('status'))
        
        # Calculate approval rate
        approved = KYCRecord.objects.filter(status=KYCRecord.Status.APPROVED).count()
        rejected = KYCRecord.objects.filter(status=KYCRecord.Status.REJECTED).count()
        
        approval_rate = 0
        if approved + rejected > 0:
            approval_rate = (approved / (approved + rejected)) * 100
        
        # Prepare report data
        report_data = {
            'date': yesterday.isoformat(),
            'total_records': total_records,
            'daily_records': daily_records,
            'approval_rate': round(approval_rate, 2),
            'status_breakdown': dict(status_breakdown.values_list('status', 'count'))
        }
        
        # Send report to admin emails
        if hasattr(settings, 'ADMIN_EMAIL_LIST'):
            subject = f'Daily KYC Report - {yesterday.strftime("%Y-%m-%d")}'
            
            html_message = render_to_string('kyc/emails/daily_report.html', {
                'report_data': report_data,
                'date': yesterday
            })
            
            for admin_email in settings.ADMIN_EMAIL_LIST:
                send_mail(
                    subject=subject,
                    message=f"Daily KYC Report for {yesterday}",
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    fail_silently=True
                )
        
        logger.info(f"Generated KYC report for {yesterday}")
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating KYC report: {str(e)}")
        raise