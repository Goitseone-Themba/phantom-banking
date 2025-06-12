from core.camunda import get_camunda_client, handle_camunda_error, complete_task_with_variables
from .models import CustomUser, SecurityEvent, EmailVerification, MerchantProfile
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging
import uuid

logger = logging.getLogger(__name__)

def start_security_workers():
    """
    Initializes all security-related Camunda workers
    """
    client = get_camunda_client()

    # Register workers for each security task
    client.subscribe('validate-kyc-data', ['user_id', 'kyc_data'], handle_validate_kyc)
    client.subscribe('process-merchant-approval', ['merchant_id'], handle_merchant_approval)
    client.subscribe('handle-suspicious-activity', ['user_id', 'event_data'], handle_suspicious_activity)
    client.subscribe('process-email-verification', ['user_id'], handle_email_verification)
    
    logger.info("Security workers started successfully")
    return client

def handle_validate_kyc(task):
    """
    Validates KYC data for a user
    """
    try:
        variables = task.get_variables()
        user_id = variables.get('user_id')
        kyc_data = variables.get('kyc_data', {})

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            
            # Validate required KYC fields
            required_fields = ['national_id', 'date_of_birth', 'phone_number']
            missing_fields = [field for field in required_fields 
                            if not kyc_data.get(field)]
            
            if missing_fields:
                handle_camunda_error(
                    task,
                    "Missing required KYC fields",
                    f"Fields missing: {', '.join(missing_fields)}"
                )
                return

            # Update user KYC status
            user.kyc_status = 'in_progress'
            user.save()

            # Log KYC validation event
            SecurityEvent.objects.create(
                user=user,
                event_type='kyc_validation',
                details={
                    'status': 'in_progress',
                    'validation_timestamp': timezone.now().isoformat()
                }
            )

        complete_task_with_variables(task, {
            'kyc_validation_success': True,
            'validation_timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        handle_camunda_error(task, "Failed to validate KYC data", str(e))

def handle_merchant_approval(task):
    """
    Processes merchant approval requests
    """
    try:
        variables = task.get_variables()
        merchant_id = variables.get('merchant_id')

        with transaction.atomic():
            merchant = CustomUser.objects.get(
                id=merchant_id,
                role='merchant'
            )
            profile = MerchantProfile.objects.get(user=merchant)

            # Update merchant status
            profile.is_approved = True
            profile.approval_date = timezone.now()
            profile.save()

            # Update user verification status
            merchant.verification_status = 'verified'
            merchant.save()

            # Send approval notification
            context = {
                'business_name': profile.business_name,
                'admin_name': profile.admin_name,
                'approval_date': profile.approval_date
            }
            
            html_message = render_to_string(
                'security/email/merchant_approval.html',
                context
            )
            
            send_mail(
                subject='Merchant Account Approved',
                message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.contact_email],
                html_message=html_message
            )

            # Log approval event
            SecurityEvent.objects.create(
                user=merchant,
                event_type='merchant_approved',
                details={
                    'business_name': profile.business_name,
                    'approval_date': profile.approval_date.isoformat()
                }
            )

        complete_task_with_variables(task, {
            'approval_success': True,
            'approval_timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        handle_camunda_error(task, "Failed to process merchant approval", str(e))

def handle_suspicious_activity(task):
    """
    Handles detected suspicious activity
    """
    try:
        variables = task.get_variables()
        user_id = variables.get('user_id')
        event_data = variables.get('event_data', {})

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            
            # Log suspicious activity
            security_event = SecurityEvent.objects.create(
                user=user,
                event_type='suspicious_activity',
                details=event_data
            )

            # Implement security measures based on event type
            if event_data.get('type') == 'multiple_failed_logins':
                user.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
                user.save()
            
            elif event_data.get('type') == 'unusual_transaction_pattern':
                # Flag account for review
                user.verification_status = 'pending'
                user.save()

            # Send notification to user
            context = {
                'user': user,
                'event_type': event_data.get('type'),
                'timestamp': timezone.now()
            }
            
            html_message = render_to_string(
                'security/email/suspicious_activity.html',
                context
            )
            
            send_mail(
                subject='Security Alert - Suspicious Activity Detected',
                message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message
            )

        complete_task_with_variables(task, {
            'handled_successfully': True,
            'security_event_id': str(security_event.id)
        })

    except Exception as e:
        handle_camunda_error(task, "Failed to handle suspicious activity", str(e))

def handle_email_verification(task):
    """
    Processes email verification requests
    """
    try:
        variables = task.get_variables()
        user_id = variables.get('user_id')

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            
            # Generate verification token
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timezone.timedelta(days=1)
            
            verification = EmailVerification.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )

            # Send verification email
            context = {
                'user': user,
                'token': token,
                'expires_at': expires_at
            }
            
            html_message = render_to_string(
                'security/email/verify_email.html',
                context
            )
            
            send_mail(
                subject='Verify Your Email Address',
                message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message
            )

            # Log verification request
            SecurityEvent.objects.create(
                user=user,
                event_type='email_verification_requested',
                details={
                    'verification_id': str(verification.id),
                    'expires_at': expires_at.isoformat()
                }
            )

        complete_task_with_variables(task, {
            'verification_sent': True,
            'verification_id': str(verification.id)
        })

    except Exception as e:
        handle_camunda_error(task, "Failed to process email verification", str(e))