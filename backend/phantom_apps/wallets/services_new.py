"""
New Wallet services for independent wallet business model
"""
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import logging

from .models import Wallet
from ..customers.models import Customer, MerchantCustomerAccess
from ..merchants.models import Merchant
from ..common.exceptions import (
    CustomerNotFoundError, 
    WalletNotFoundError,
    PhantomBankingException,
    PhantomBankingErrorCodes
)

logger = logging.getLogger('phantom_apps')


class InteroperableWalletService:
    """Service class for interoperable wallet operations"""
    
    @staticmethod
    def create_or_get_wallet(merchant, customer_phone_or_id):
        """
        Create wallet for customer or return existing wallet
        Access is automatically granted for wallet creators, but can only be modified by admin
        
        Args:
            merchant: Merchant instance from JWT token
            customer_phone_or_id: Phone number or UUID of the customer
            
        Returns:
            tuple: (wallet_instance, created_boolean, access_info)
            
        Raises:
            CustomerNotFoundError: If customer doesn't exist
            PhantomBankingException: For other errors
        """
        try:
            # Find or create customer
            customer = InteroperableWalletService._get_or_create_customer(
                customer_phone_or_id, merchant
            )
            
            # Check if wallet already exists
            try:
                existing_wallet = Wallet.objects.get(customer=customer)
                logger.info(f"Found existing wallet {existing_wallet.wallet_id} for customer {customer.customer_id}")
                
                # Check existing access (don't modify, just return info)
                access_info = InteroperableWalletService._get_merchant_access_info(
                    merchant, customer
                )
                
                return existing_wallet, False, access_info
                
            except Wallet.DoesNotExist:
                # Create new wallet and auto-grant access to creator
                return InteroperableWalletService._create_new_wallet(
                    merchant, customer
                )
                
        except CustomerNotFoundError:
            # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating wallet: {e}")
            raise PhantomBankingException(
                message="Wallet creation failed due to internal error",
                error_code=PhantomBankingErrorCodes.WALLET_CREATION_FAILED
            )
    
    @staticmethod
    def _get_or_create_customer(phone_or_id, merchant):
        """
        Get or create customer by phone number or ID
        """
        # Try to find by phone number first
        if len(str(phone_or_id)) <= 15:  # Assume it's a phone number
            try:
                customer = Customer.objects.get(phone_number=phone_or_id)
                return customer
            except Customer.DoesNotExist:
                # Customer doesn't exist, this would require additional customer info
                # For now, raise an error - in production, you'd want to create the customer
                raise CustomerNotFoundError(phone_or_id)
        else:
            # Try to find by UUID
            try:
                customer = Customer.objects.get(customer_id=phone_or_id)
                return customer
            except Customer.DoesNotExist:
                raise CustomerNotFoundError(phone_or_id)
    
    @staticmethod
    def _auto_grant_wallet_creator_access(merchant, customer):
        """
        Automatically grant access to merchant who creates a wallet
        This is the only case where merchants can get access without admin approval
        """
        access, created = MerchantCustomerAccess.objects.get_or_create(
            merchant=merchant,
            customer=customer,
            defaults={
                'access_type': 'full',
                'grant_reason': 'wallet_creation',
                'created_by_merchant': merchant,
                'is_active': True
            }
        )
        
        if created:
            logger.info(f"Auto-granted full access to wallet creator {merchant.merchant_id} for customer {customer.customer_id}")
        
        return created
    
    @staticmethod
    def _get_merchant_access_info(merchant, customer):
        """
        Get access information for a merchant to a customer's wallet
        """
        try:
            access = MerchantCustomerAccess.objects.get(
                merchant=merchant,
                customer=customer,
                is_active=True
            )
            return {
                'has_access': access.is_valid,
                'access_type': access.access_type,
                'can_debit': access.access_type in ['full'],
                'can_credit': access.access_type in ['full', 'credit_only'],
                'can_view': access.access_type in ['full', 'credit_only', 'view_only'],
                'granted_at': access.granted_at,
                'expires_at': access.expires_at,
                'grant_reason': access.grant_reason
            }
        except MerchantCustomerAccess.DoesNotExist:
            return {
                'has_access': False,
                'access_type': 'none',
                'can_debit': False,
                'can_credit': False,
                'can_view': False,
                'message': 'No access granted. Contact administrator for access.'
            }
    
    @staticmethod
    @transaction.atomic
    def _create_new_wallet(merchant, customer):
        """
        Create a new wallet with default settings
        Auto-grants full access to the wallet creator
        
        Args:
            merchant: Merchant instance
            customer: Customer instance
            
        Returns:
            tuple: (wallet_instance, True, access_info)
        """
        try:
            # Get default limits from settings
            phantom_settings = getattr(settings, 'PHANTOM_BANKING_SETTINGS', {})
            daily_limit = Decimal(str(phantom_settings.get('WALLET_DAILY_LIMIT', 50000.00)))
            monthly_limit = Decimal(str(phantom_settings.get('WALLET_MONTHLY_LIMIT', 200000.00)))
            default_currency = phantom_settings.get('DEFAULT_CURRENCY', 'BWP')
            
            # Create wallet
            wallet = Wallet.objects.create(
                customer=customer,
                created_by_merchant=merchant,
                balance=Decimal('0.00'),
                currency=default_currency,
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
                status='active',
                is_frozen=False
            )
            
            # Auto-grant full access to the creating merchant
            access_granted = InteroperableWalletService._auto_grant_wallet_creator_access(
                merchant, customer
            )
            
            # Get access info to return
            access_info = {
                'has_access': True,
                'access_type': 'full',
                'can_debit': True,
                'can_credit': True,
                'can_view': True,
                'grant_reason': 'wallet_creation',
                'granted_at': timezone.now()
            }
            
            logger.info(f"Created new wallet {wallet.wallet_id} for customer {customer.customer_id}")
            return wallet, True, access_info
            
        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            raise PhantomBankingException(
                message="Failed to create wallet",
                error_code=PhantomBankingErrorCodes.WALLET_CREATION_FAILED
            )
    
    @staticmethod
    def get_accessible_wallets(merchant, status_filter=None, customer_name_filter=None, 
                             page=1, page_size=20):
        """
        Get paginated list of wallets accessible by a merchant
        
        Args:
            merchant: Merchant instance
            status_filter: Filter by wallet status (default: 'active')
            customer_name_filter: Filter by customer name
            page: Page number (default: 1)
            page_size: Items per page (default: 20)
            
        Returns:
            dict: {
                'wallets': list of wallet instances,
                'access_info': dict mapping wallet_id to access info,
                'total_count': total number of wallets,
                'page_count': total number of pages,
                'current_page': current page number,
                'has_next': boolean,
                'has_previous': boolean
            }
        """
        try:
            # Get all accessible customers through MerchantCustomerAccess
            accessible_customers = Customer.objects.filter(
                merchant_access__merchant=merchant,
                merchant_access__is_active=True
            ).distinct()
            
            # Get wallets for these customers
            queryset = Wallet.objects.filter(
                customer__in=accessible_customers
            ).select_related('customer').prefetch_related(
                'customer__merchant_access'
            )
            
            # Apply status filter (default to active only)
            if status_filter is None:
                status_filter = 'active'
            
            if status_filter and status_filter != 'all':
                queryset = queryset.filter(status=status_filter)
            
            # Apply customer name filter
            if customer_name_filter:
                queryset = queryset.filter(
                    customer__first_name__icontains=customer_name_filter
                ) | queryset.filter(
                    customer__last_name__icontains=customer_name_filter
                )
            
            # Order by creation date (newest first)
            queryset = queryset.order_by('-created_at')
            
            # Get total count
            total_count = queryset.count()
            
            # Calculate pagination values
            page_count = (total_count + page_size - 1) // page_size if total_count > 0 else 1
            has_next = page < page_count
            has_previous = page > 1
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            wallets = queryset[start:end]
            
            # Get access information for each wallet
            access_info = {}
            for wallet in wallets:
                try:
                    access = MerchantCustomerAccess.objects.get(
                        merchant=merchant,
                        customer=wallet.customer,
                        is_active=True
                    )
                    access_info[str(wallet.wallet_id)] = {
                        'access_type': access.access_type,
                        'granted_at': access.granted_at,
                        'expires_at': access.expires_at,
                        'can_debit': access.access_type in ['full'],
                        'can_credit': access.access_type in ['full', 'credit_only'],
                        'can_view': True  # All have view access
                    }
                except MerchantCustomerAccess.DoesNotExist:
                    access_info[str(wallet.wallet_id)] = {
                        'access_type': 'none',
                        'can_debit': False,
                        'can_credit': False,
                        'can_view': False
                    }
            
            result = {
                'wallets': list(wallets),
                'access_info': access_info,
                'total_count': total_count,
                'page_count': page_count,
                'current_page': page,
                'has_next': has_next,
                'has_previous': has_previous,
                'page_size': page_size
            }
            
            logger.info(f"Retrieved {len(wallets)} accessible wallets for merchant {merchant.merchant_id} (page {page})")
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error getting accessible wallets: {e}")
            raise PhantomBankingException(
                message="Failed to retrieve accessible wallets",
                error_code=PhantomBankingErrorCodes.DATABASE_ERROR
            )
    
    @staticmethod
    def get_customer_wallet_by_phone(customer_phone, authenticated_merchant=None):
        """
        Get wallet for a customer by phone number
        
        Args:
            customer_phone: Customer's phone number
            authenticated_merchant: Merchant instance (for access check)
            
        Returns:
            dict: {
                'wallet': Wallet instance,
                'access_info': access information for the merchant
            }
            
        Raises:
            CustomerNotFoundError: If customer doesn't exist
            WalletNotFoundError: If customer has no wallet
        """
        try:
            # Find customer by phone
            try:
                customer = Customer.objects.get(phone_number=customer_phone)
            except Customer.DoesNotExist:
                logger.warning(f"Customer with phone {customer_phone} not found")
                raise CustomerNotFoundError(customer_phone)
            
            # Get customer's wallet
            try:
                wallet = Wallet.objects.select_related('customer').get(
                    customer=customer
                )
            except Wallet.DoesNotExist:
                logger.warning(f"No wallet found for customer {customer_phone}")
                raise WalletNotFoundError(customer_id=customer.customer_id)
            
            # Get access information if merchant is provided
            access_info = None
            if authenticated_merchant:
                try:
                    access = MerchantCustomerAccess.objects.get(
                        merchant=authenticated_merchant,
                        customer=customer,
                        is_active=True
                    )
                    access_info = {
                        'has_access': access.is_valid,
                        'access_type': access.access_type,
                        'can_debit': access.access_type in ['full'],
                        'can_credit': access.access_type in ['full', 'credit_only'],
                        'can_view': True,
                        'granted_at': access.granted_at,
                        'expires_at': access.expires_at
                    }
                except MerchantCustomerAccess.DoesNotExist:
                    access_info = {
                        'has_access': False,
                        'access_type': 'none',
                        'can_debit': False,
                        'can_credit': False,
                        'can_view': False
                    }
            
            logger.info(f"Retrieved wallet {wallet.wallet_id} for customer {customer_phone}")
            return {
                'wallet': wallet,
                'access_info': access_info
            }
            
        except (CustomerNotFoundError, WalletNotFoundError):
            # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting customer wallet: {e}")
            raise PhantomBankingException(
                message="Failed to retrieve customer wallet",
                error_code=PhantomBankingErrorCodes.DATABASE_ERROR
            )

