"""
Enhanced Transaction services for independent wallet business model
"""
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal
import logging
import uuid

from .models import Transaction, PaymentMethod, TransactionStatus
from ..wallets.models import Wallet
from ..customers.models import Customer, MerchantCustomerAccess
from ..merchants.models import Merchant
from ..common.exceptions import (
    PhantomBankingException,
    PhantomBankingErrorCodes,
    WalletNotFoundError,
    InsufficientFundsError
)

logger = logging.getLogger('phantom_apps')


class InteroperableTransactionService:
    """Enhanced transaction service for interoperable wallets"""
    
    @staticmethod
    def process_wallet_debit(merchant, customer_phone, amount, transaction_type='merchant_debit', 
                           description=None, reference=None, payment_method_code='wallet'):
        """
        Process a debit transaction from customer's wallet
        
        Args:
            merchant: Merchant instance
            customer_phone: Customer's phone number
            amount: Amount to debit
            transaction_type: Type of transaction
            description: Transaction description
            reference: Transaction reference
            payment_method_code: Payment method code
            
        Returns:
            Transaction instance
            
        Raises:
            WalletNotFoundError: If wallet doesn't exist
            InsufficientFundsError: If insufficient balance
            PhantomBankingException: For access control violations
        """
        try:
            # Get customer and wallet
            customer = Customer.objects.get(phone_number=customer_phone)
            wallet = Wallet.objects.get(customer=customer)
            
            # Check merchant access
            if not wallet.merchant_has_access(merchant, 'full'):
                raise PhantomBankingException(
                    message="Merchant does not have debit access to this wallet",
                    error_code=PhantomBankingErrorCodes.PERMISSION_DENIED
                )
            
            # Check balance
            if wallet.balance < Decimal(str(amount)):
                raise InsufficientFundsError(
                    f"Insufficient funds. Available: {wallet.balance}, Required: {amount}"
                )
            
            # Process transaction
            with db_transaction.atomic():
                # Record balance before
                balance_before = wallet.balance
                
                # Update wallet balance
                wallet.balance -= Decimal(str(amount))
                wallet.save(update_fields=['balance', 'updated_at'])
                
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    transaction_type=transaction_type,
                    direction='debit',
                    amount=amount,
                    wallet=wallet,
                    customer=customer,
                    merchant=merchant,
                    status=InteroperableTransactionService._get_status('completed'),
                    payment_method=InteroperableTransactionService._get_payment_method(payment_method_code),
                    description=description or f"Debit by {merchant.business_name}",
                    reference=reference or f"DEB_{str(uuid.uuid4())[:8]}",
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                    completed_at=timezone.now(),
                    metadata={
                        'merchant_access_type': 'full',
                        'initiated_by': 'merchant'
                    }
                )
                
                logger.info(f"Debit processed: {transaction_obj.transaction_id} for amount {amount}")
                return transaction_obj
                
        except Customer.DoesNotExist:
            raise WalletNotFoundError(f"Customer with phone {customer_phone} not found")
        except Wallet.DoesNotExist:
            raise WalletNotFoundError(f"No wallet found for customer {customer_phone}")
        except (InsufficientFundsError, PhantomBankingException):
            raise
        except Exception as e:
            logger.error(f"Error processing debit: {e}")
            raise PhantomBankingException(
                message="Failed to process debit transaction",
                error_code=PhantomBankingErrorCodes.TRANSACTION_FAILED
            )
    
    @staticmethod
    def process_wallet_credit(merchant, customer_phone, amount, transaction_type='merchant_credit',
                            description=None, reference=None, payment_method_code='wallet'):
        """
        Process a credit transaction to customer's wallet
        
        Args:
            merchant: Merchant instance
            customer_phone: Customer's phone number
            amount: Amount to credit
            transaction_type: Type of transaction
            description: Transaction description
            reference: Transaction reference
            payment_method_code: Payment method code
            
        Returns:
            Transaction instance
        """
        try:
            # Get customer and wallet
            customer = Customer.objects.get(phone_number=customer_phone)
            wallet = Wallet.objects.get(customer=customer)
            
            # Check merchant access (credit_only or full)
            if not wallet.merchant_has_access(merchant, 'credit_only'):
                raise PhantomBankingException(
                    message="Merchant does not have credit access to this wallet",
                    error_code=PhantomBankingErrorCodes.PERMISSION_DENIED
                )
            
            # Process transaction
            with db_transaction.atomic():
                # Record balance before
                balance_before = wallet.balance
                
                # Update wallet balance
                wallet.balance += Decimal(str(amount))
                wallet.save(update_fields=['balance', 'updated_at'])
                
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    transaction_type=transaction_type,
                    direction='credit',
                    amount=amount,
                    wallet=wallet,
                    customer=customer,
                    merchant=merchant,
                    status=InteroperableTransactionService._get_status('completed'),
                    payment_method=InteroperableTransactionService._get_payment_method(payment_method_code),
                    description=description or f"Credit by {merchant.business_name}",
                    reference=reference or f"CRD_{str(uuid.uuid4())[:8]}",
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                    completed_at=timezone.now(),
                    metadata={
                        'merchant_access_type': wallet.get_accessible_merchants().filter(
                            merchant=merchant
                        ).first().access_type if wallet.get_accessible_merchants().filter(
                            merchant=merchant
                        ).exists() else 'unknown',
                        'initiated_by': 'merchant'
                    }
                )
                
                logger.info(f"Credit processed: {transaction_obj.transaction_id} for amount {amount}")
                return transaction_obj
                
        except Customer.DoesNotExist:
            raise WalletNotFoundError(f"Customer with phone {customer_phone} not found")
        except Wallet.DoesNotExist:
            raise WalletNotFoundError(f"No wallet found for customer {customer_phone}")
        except PhantomBankingException:
            raise
        except Exception as e:
            logger.error(f"Error processing credit: {e}")
            raise PhantomBankingException(
                message="Failed to process credit transaction",
                error_code=PhantomBankingErrorCodes.TRANSACTION_FAILED
            )
    
    @staticmethod
    def get_customer_transactions(customer_phone, merchant=None, limit=50):
        """
        Get transaction history for a customer
        
        Args:
            customer_phone: Customer's phone number
            merchant: Optional merchant filter (for merchant-specific view)
            limit: Maximum number of transactions to return
            
        Returns:
            QuerySet of Transaction objects
        """
        try:
            customer = Customer.objects.get(phone_number=customer_phone)
            
            queryset = Transaction.objects.filter(
                customer=customer
            ).select_related(
                'wallet', 'merchant', 'status', 'payment_method'
            ).order_by('-created_at')
            
            # If merchant is specified, only show transactions they have access to
            if merchant:
                # Check if merchant has access to this customer's wallet
                try:
                    access = MerchantCustomerAccess.objects.get(
                        merchant=merchant,
                        customer=customer,
                        is_active=True
                    )
                    # Merchant can only see transactions they initiated
                    queryset = queryset.filter(merchant=merchant)
                except MerchantCustomerAccess.DoesNotExist:
                    # No access, return empty queryset
                    return Transaction.objects.none()
            
            return queryset[:limit]
            
        except Customer.DoesNotExist:
            return Transaction.objects.none()
    
    @staticmethod
    def get_merchant_transaction_summary(merchant, date_from=None, date_to=None):
        """
        Get transaction summary for a merchant across all accessible wallets
        
        Args:
            merchant: Merchant instance
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            dict: Summary statistics
        """
        # Get all transactions initiated by this merchant
        transactions = Transaction.objects.filter(
            merchant=merchant
        ).select_related('status', 'payment_method')
        
        if date_from:
            transactions = transactions.filter(created_at__gte=date_from)
        if date_to:
            transactions = transactions.filter(created_at__lte=date_to)
        
        # Calculate summaries
        total_transactions = transactions.count()
        total_debits = transactions.filter(direction='debit').count()
        total_credits = transactions.filter(direction='credit').count()
        
        total_debit_amount = sum(
            t.amount for t in transactions.filter(direction='debit')
        )
        total_credit_amount = sum(
            t.amount for t in transactions.filter(direction='credit')
        )
        
        # Get unique customers served
        unique_customers = transactions.values('customer').distinct().count()
        
        # Get transaction types breakdown
        transaction_types = {}
        for t_type, _ in Transaction.TYPE_CHOICES:
            count = transactions.filter(transaction_type=t_type).count()
            if count > 0:
                transaction_types[t_type] = count
        
        # Recent transactions
        recent_transactions = transactions.order_by('-created_at')[:10]
        recent = [{
            'transaction_id': str(t.transaction_id),
            'amount': float(t.amount),
            'direction': t.direction,
            'transaction_type': t.transaction_type,
            'customer_phone': t.customer.phone_number,
            'status': t.status.code if t.status else 'unknown',
            'created_at': t.created_at.isoformat()
        } for t in recent_transactions]
        
        return {
            'summary': {
                'total_transactions': total_transactions,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'total_debit_amount': float(total_debit_amount),
                'total_credit_amount': float(total_credit_amount),
                'net_amount': float(total_credit_amount - total_debit_amount),
                'unique_customers_served': unique_customers
            },
            'transaction_types': transaction_types,
            'recent_transactions': recent
        }
    
    @staticmethod
    def get_accessible_wallet_transactions(merchant, wallet_id, limit=50):
        """
        Get transactions for a specific wallet that merchant has access to
        
        Args:
            merchant: Merchant instance
            wallet_id: Wallet UUID
            limit: Maximum number of transactions
            
        Returns:
            QuerySet of Transaction objects
        """
        try:
            wallet = Wallet.objects.get(wallet_id=wallet_id)
            
            # Check access
            if not wallet.merchant_has_access(merchant, 'view_only'):
                raise PhantomBankingException(
                    message="Merchant does not have access to this wallet",
                    error_code=PhantomBankingErrorCodes.PERMISSION_DENIED
                )
            
            # Return only transactions initiated by this merchant
            return Transaction.objects.filter(
                wallet=wallet,
                merchant=merchant
            ).select_related(
                'status', 'payment_method'
            ).order_by('-created_at')[:limit]
            
        except Wallet.DoesNotExist:
            raise WalletNotFoundError(f"Wallet {wallet_id} not found")
    
    @staticmethod
    def _get_status(status_code):
        """Get or create transaction status"""
        status, created = TransactionStatus.objects.get_or_create(
            code=status_code,
            defaults={'name': status_code.replace('_', ' ').title()}
        )
        return status
    
    @staticmethod
    def _get_payment_method(method_code):
        """Get or create payment method"""
        method, created = PaymentMethod.objects.get_or_create(
            code=method_code,
            defaults={'name': method_code.replace('_', ' ').title()}
        )
        return method

