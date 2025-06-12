from core.camunda import get_camunda_client, handle_camunda_error, complete_task_with_variables
from .models import WalletCreationRequest, Wallet, WalletAuditLog
from security.models import CustomUser, SecurityEvent
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def start_wallet_workers():
    """
    Initializes all wallet-related Camunda workers
    """
    client = get_camunda_client()

    # Register workers for each task
    client.subscribe('validate-wallet-request', ['merchant_id', 'request_data'], handle_validate_wallet_request)
    client.subscribe('create-wallet', ['request_id'], handle_create_wallet)
    client.subscribe('notify-wallet-creation', ['wallet_id'], handle_notify_wallet_creation)
    
    logger.info("Wallet workers started successfully")
    return client

def handle_validate_wallet_request(task):
    """
    Validates the wallet creation request data
    """
    try:
        variables = task.get_variables()
        merchant_id = variables.get('merchant_id')
        request_data = variables.get('request_data', {})

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 
                         'national_id', 'date_of_birth']
        
        missing_fields = [field for field in required_fields 
                         if not request_data.get(field)]
        
        if missing_fields:
            handle_camunda_error(
                task,
                "Missing required fields",
                f"Fields missing: {', '.join(missing_fields)}"
            )
            return

        # Create WalletCreationRequest
        with transaction.atomic():
            request = WalletCreationRequest.objects.create(
                merchant_id=merchant_id,
                **request_data
            )
            
            # Log security event
            SecurityEvent.objects.create(
                event_type='wallet_request_created',
                user_id=merchant_id,
                details={
                    'request_id': str(request.request_id),
                    'email': request_data['email']
                }
            )

        complete_task_with_variables(task, {
            'request_id': str(request.request_id),
            'validation_success': True
        })

    except Exception as e:
        handle_camunda_error(task, "Failed to validate wallet request", str(e))

def handle_create_wallet(task):
    """
    Creates a new wallet based on the validated request
    """
    try:
        variables = task.get_variables()
        request_id = variables.get('request_id')
        
        with transaction.atomic():
            # Get the wallet request
            request = WalletCreationRequest.objects.get(request_id=request_id)
            
            # Create or get user
            user, created = CustomUser.objects.get_or_create(
                email=request.email,
                defaults={
                    'username': request.email.split('@')[0],
                    'first_name': request.first_name,
                    'last_name': request.last_name,
                    'phone_number': request.phone_number,
                    'national_id': request.national_id,
                    'date_of_birth': request.date_of_birth,
                    'role': 'customer'
                }
            )

            # Create wallet
            wallet = Wallet.objects.create(
                wallet_id=f"W{timezone.now().strftime('%Y%m%d')}{user.id}",
                user=user,
                merchant=request.merchant,
                wallet_type='basic'
            )

            # Create audit log
            WalletAuditLog.objects.create(
                wallet=wallet,
                action='create',
                actor=request.merchant,
                details={
                    'request_id': str(request_id),
                    'created_by': request.merchant.username
                },
                ip_address='0.0.0.0'  # This should be passed from the request
            )

        complete_task_with_variables(task, {
            'wallet_id': wallet.wallet_id,
            'creation_success': True
        })

    except Exception as e:
        handle_camunda_error(task, "Failed to create wallet", str(e))

def handle_notify_wallet_creation(task):
    """
    Sends notifications about the wallet creation
    """
    try:
        variables = task.get_variables()
        wallet_id = variables.get('wallet_id')
        
        wallet = Wallet.objects.get(wallet_id=wallet_id)
        request = WalletCreationRequest.objects.get(
            email=wallet.user.email,
            merchant=wallet.merchant
        )
        
        # Send notification email
        request.send_notification_email()
        
        # Log the notification
        SecurityEvent.objects.create(
            user=wallet.user,
            event_type='wallet_creation_notification',
            details={
                'wallet_id': wallet_id,
                'notification_type': 'email',
                'sent_to': wallet.user.email
            }
        )

        complete_task_with_variables(task, {
            'notification_sent': True
        })

    except Exception as e:
        handle_camunda_error(task, "Failed to send wallet creation notification", str(e))