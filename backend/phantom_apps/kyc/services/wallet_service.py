import logging
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)

class WalletService:
    """
    Service to handle wallet upgrades after successful KYC
    """
    
    def upgrade_wallet_after_kyc(self, user: User):
        """
        Upgrade user's wallet after successful KYC verification
        """
        try:
            with transaction.atomic():
                # Import your existing wallet model - adjust path as needed
                from ...wallets.models import Wallet  # Adjust this import path
                
                # Get or create wallet for the user
                wallet, created = Wallet.objects.get_or_create(
                    user=user,
                    defaults={
                        'wallet_type': 'basic',
                        'balance': 0,
                        'is_active': True,
                        'created_at': timezone.now()
                    }
                )
                
                # Upgrade wallet to premium/verified status
                if hasattr(wallet, 'wallet_type'):
                    wallet.wallet_type = 'verified'  # or 'premium'
                
                if hasattr(wallet, 'daily_limit'):
                    wallet.daily_limit = 50000  # Increased limit after KYC
                
                if hasattr(wallet, 'monthly_limit'):
                    wallet.monthly_limit = 500000  # Increased monthly limit
                
                if hasattr(wallet, 'is_kyc_verified'):
                    wallet.is_kyc_verified = True
                
                if hasattr(wallet, 'upgraded_at'):
                    wallet.upgraded_at = timezone.now()
                
                wallet.save()
                
                # Create wallet upgrade event/transaction
                self._create_wallet_upgrade_event(wallet, user)
                
                # Send notification to user
                self._send_upgrade_notification(user)
                
                logger.info(f"Wallet upgraded successfully for user {user.id}")
                return True, wallet
                
        except Exception as e:
            logger.error(f"Failed to upgrade wallet for user {user.id}: {str(e)}")
            return False, str(e)
    
    def _create_wallet_upgrade_event(self, wallet, user):
        """Create an event record for wallet upgrade"""
        try:
            # If you have a transaction or event model
            from ...transactions.models import Transaction  # Adjust path
            
            Transaction.objects.create(
                user=user,
                wallet=wallet,
                transaction_type='WALLET_UPGRADE',
                amount=0,
                description='Wallet upgraded after KYC verification',
                status='COMPLETED',
                metadata={'upgrade_reason': 'kyc_verified'}
            )
        except Exception as e:
            logger.warning(f"Could not create wallet upgrade event: {str(e)}")
    
    def _send_upgrade_notification(self, user):
        """Send notification to user about wallet upgrade"""
        try:
            # If you have a notification system
            from ...notifications.models import Notification  # Adjust path
            
            Notification.objects.create(
                user=user,
                title='Wallet Upgraded!',
                message='Your wallet has been successfully upgraded after KYC verification. You now have access to higher transaction limits.',
                notification_type='WALLET_UPGRADE',
                is_read=False
            )
        except Exception as e:
            logger.warning(f"Could not send upgrade notification: {str(e)}")