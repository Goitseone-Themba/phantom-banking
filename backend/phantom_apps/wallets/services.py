"""
Wallet business logic services
"""
from django.db import transaction
from django.conf import settings
from decimal import Decimal
import logging

from .models import Wallet
from ..customers.models import Customer
from ..merchants.models import Merchant
from ..common.exceptions import (
    CustomerNotFoundError, 
    CustomerNotOwnedError,
    WalletNotFoundError,
    MerchantHasNoWalletsError,
    PhantomBankingException,
    PhantomBankingErrorCodes
)

logger = logging.getLogger('phantom_apps')

class WalletService:
    """Service class for wallet operations"""
    
    @staticmethod
    def create_or_get_wallet(merchant, customer_id):
        """
        Create wallet for customer or return existing wallet
        
        Args:
            merchant: Merchant instance from JWT token
            customer_id: UUID of the customer
            
        Returns:
            tuple: (wallet_instance, created_boolean)
            
        Raises:
            CustomerNotFoundError: If customer doesn't exist
            CustomerNotOwnedError: If customer doesn't belong to merchant
            PhantomBankingException: For other errors
        """
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                logger.warning(f"Customer {customer_id} not found")
                raise CustomerNotFoundError(customer_id)
            
            # Validate customer belongs to merchant
            if customer.merchant != merchant:
                logger.warning(f"Customer {customer_id} not owned by merchant {merchant.merchant_id}")
                raise CustomerNotOwnedError(customer_id, merchant.merchant_id)
            
            # Check if wallet already exists
            try:
                existing_wallet = Wallet.objects.get(
                    customer=customer,
                    merchant=merchant
                )
                logger.info(f"Returning existing wallet {existing_wallet.wallet_id} for customer {customer_id}")
                return existing_wallet, False
                
            except Wallet.DoesNotExist:
                # Create new wallet
                return WalletService._create_new_wallet(merchant, customer)
                
        except (CustomerNotFoundError, CustomerNotOwnedError):
            # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating wallet: {e}")
            raise PhantomBankingException(
                message="Wallet creation failed due to internal error",
                error_code=PhantomBankingErrorCodes.WALLET_CREATION_FAILED
            )
    
    @staticmethod
    @transaction.atomic
    def _create_new_wallet(merchant, customer):
        """
        Create a new wallet with default settings
        
        Args:
            merchant: Merchant instance
            customer: Customer instance
            
        Returns:
            tuple: (wallet_instance, True)
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
                merchant=merchant,
                balance=Decimal('0.00'),
                currency=default_currency,
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
                status='active',
                is_frozen=False
            )
            
            logger.info(f"Created new wallet {wallet.wallet_id} for customer {customer.customer_id}")
            return wallet, True
            
        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            raise PhantomBankingException(
                message="Failed to create wallet",
                error_code=PhantomBankingErrorCodes.WALLET_CREATION_FAILED
            )

class CustomerAssociationService:
    """Service class for customer-wallet association operations"""
    
    @staticmethod
    def get_customer_wallet(customer_id, authenticated_merchant=None):
        """
        Get wallet for a specific customer
        
        Args:
            customer_id: UUID of the customer
            authenticated_merchant: Merchant instance from JWT (optional for permission check)
            
        Returns:
            Wallet instance
            
        Raises:
            CustomerNotFoundError: If customer doesn't exist
            CustomerNotOwnedError: If customer doesn't belong to merchant
            WalletNotFoundError: If customer has no wallet
        """
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                logger.warning(f"Customer {customer_id} not found")
                raise CustomerNotFoundError(customer_id)
            
            # Validate customer belongs to authenticated merchant (if provided)
            if authenticated_merchant and customer.merchant != authenticated_merchant:
                logger.warning(f"Customer {customer_id} not owned by merchant {authenticated_merchant.merchant_id}")
                raise CustomerNotOwnedError(customer_id, authenticated_merchant.merchant_id)
            
            # Get customer's wallet
            try:
                wallet = Wallet.objects.select_related('customer', 'merchant').get(
                    customer=customer
                )
                logger.info(f"Retrieved wallet {wallet.wallet_id} for customer {customer_id}")
                return wallet
                
            except Wallet.DoesNotExist:
                logger.warning(f"No wallet found for customer {customer_id}")
                raise WalletNotFoundError(customer_id=customer_id)
                
        except (CustomerNotFoundError, CustomerNotOwnedError, WalletNotFoundError):
            # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting customer wallet: {e}")
            raise PhantomBankingException(
                message="Failed to retrieve customer wallet",
                error_code=PhantomBankingErrorCodes.DATABASE_ERROR
            )
    
    @staticmethod
    def get_merchant_wallets(merchant, status_filter=None, customer_name_filter=None, 
                           page=1, page_size=20):
        """
        Get paginated list of wallets for a merchant
        
        Args:
            merchant: Merchant instance
            status_filter: Filter by wallet status (default: 'active')
            customer_name_filter: Filter by customer name
            page: Page number (default: 1)
            page_size: Items per page (default: 20)
            
        Returns:
            dict: {
                'wallets': list of wallet instances,
                'total_count': total number of wallets,
                'page_count': total number of pages,
                'current_page': current page number,
                'has_next': boolean,
                'has_previous': boolean
            }
            
        Raises:
            MerchantHasNoWalletsError: If merchant has no wallets
        """
        try:
            # Build queryset
            queryset = Wallet.objects.select_related('customer', 'merchant').filter(
                merchant=merchant
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
            
            # Check if merchant has any wallets
            total_count = queryset.count()
            if total_count == 0:
                logger.warning(f"Merchant {merchant.merchant_id} has no wallets")
                raise MerchantHasNoWalletsError(merchant.merchant_id)
            
            # Paginate results
            paginator = Paginator(queryset, page_size)
            
            # Validate page number
            if page > paginator.num_pages:
                page = paginator.num_pages
            elif page < 1:
                page = 1
            
            page_obj = paginator.page(page)
            
            result = {
                'wallets': list(page_obj.object_list),
                'total_count': total_count,
                'page_count': paginator.num_pages,
                'current_page': page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'page_size': page_size
            }
            
            logger.info(f"Retrieved {len(page_obj.object_list)} wallets for merchant {merchant.merchant_id} (page {page})")
            return result
            
        except MerchantHasNoWalletsError:
            # Re-raise custom exception
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting merchant wallets: {e}")
            raise PhantomBankingException(
                message="Failed to retrieve merchant wallets",
                error_code=PhantomBankingErrorCodes.DATABASE_ERROR
            )

    @staticmethod
    def verify_data_integrity(merchant):
        """
        Verify data integrity for merchant's customers and wallets
        
        Args:
            merchant: Merchant instance
            
        Returns:
            dict: Integrity check results
        """
        try:
            results = {
                'merchant_id': merchant.merchant_id,
                'business_name': merchant.business_name,
                'checks': {},
                'issues': [],
                'summary': {}
            }
            
            # Check 1: Customers count
            customers = Customer.objects.filter(merchant=merchant)
            customers_count = customers.count()
            results['checks']['customers_count'] = customers_count
            
            # Check 2: Wallets count
            wallets = Wallet.objects.filter(merchant=merchant)
            wallets_count = wallets.count()
            results['checks']['wallets_count'] = wallets_count
            
            # Check 3: Customers without wallets
            customers_without_wallets = customers.filter(wallet__isnull=True)
            customers_without_wallets_count = customers_without_wallets.count()
            results['checks']['customers_without_wallets'] = customers_without_wallets_count
            
            if customers_without_wallets_count > 0:
                results['issues'].append({
                    'type': 'customers_without_wallets',
                    'count': customers_without_wallets_count,
                    'customer_ids': [str(c.customer_id) for c in customers_without_wallets[:5]]
                })
            
            # Check 4: Orphaned wallets (wallets without customers - shouldn't happen)
            orphaned_wallets = wallets.filter(customer__isnull=True)
            orphaned_wallets_count = orphaned_wallets.count()
            results['checks']['orphaned_wallets'] = orphaned_wallets_count
            
            if orphaned_wallets_count > 0:
                results['issues'].append({
                    'type': 'orphaned_wallets',
                    'count': orphaned_wallets_count,
                    'wallet_ids': [str(w.wallet_id) for w in orphaned_wallets]
                })
            
            # Check 5: Wallets with different merchant than customer's merchant
            mismatched_merchant_wallets = wallets.exclude(customer__merchant=merchant)
            mismatched_count = mismatched_merchant_wallets.count()
            results['checks']['mismatched_merchant_wallets'] = mismatched_count
            
            if mismatched_count > 0:
                results['issues'].append({
                    'type': 'mismatched_merchant_wallets',
                    'count': mismatched_count,
                    'wallet_ids': [str(w.wallet_id) for w in mismatched_merchant_wallets]
                })
            
            # Summary
            results['summary'] = {
                'healthy': len(results['issues']) == 0,
                'issues_count': len(results['issues']),
                'customers_to_wallets_ratio': f"{wallets_count}/{customers_count}" if customers_count > 0 else "0/0"
            }
            
            logger.info(f"Data integrity check completed for merchant {merchant.merchant_id}: {len(results['issues'])} issues found")
            return results
            
        except Exception as e:
            logger.error(f"Data integrity check failed: {e}")
            raise PhantomBankingException(
                message="Data integrity verification failed",
                error_code=PhantomBankingErrorCodes.DATABASE_ERROR
            )
