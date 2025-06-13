import json
import qrcode
import requests
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from typing import Optional, Dict, Any
import logging
import uuid

from ..common.exceptions import (
    PhantomBankingException,
    PhantomBankingErrorCodes,
    WalletNotFoundError,
    InsufficientFundsError
)
from ..wallets.models import Wallet
from .models import Transaction, PaymentMethod, TransactionStatus, QRCode, EFTPayment
from ..merchants.models import Merchant
from ..customers.models import Customer

logger = logging.getLogger('phantom_apps')


class TransactionService:
    """Service class for general transaction processing"""
    
    @staticmethod
    def get_or_create_payment_method(code, name=None):
        """Get or create a payment method"""
        payment_method, created = PaymentMethod.objects.get_or_create(
            code=code,
            defaults={'name': name or code.replace('_', ' ').title()}
        )
        return payment_method
    
    @staticmethod
    def get_transaction_status(code):
        """Get a transaction status by code"""
        try:
            return TransactionStatus.objects.get(code=code)
        except TransactionStatus.DoesNotExist:
            # Create default statuses if they don't exist
            default_statuses = [
                ('pending', 'Pending'),
                ('completed', 'Completed'),
                ('failed', 'Failed'),
                ('cancelled', 'Cancelled'),
                ('processing', 'Processing'),
            ]
            for status_code, status_name in default_statuses:
                TransactionStatus.objects.get_or_create(
                    code=status_code,
                    defaults={'name': status_name}
                )
            return TransactionStatus.objects.get(code=code)
    
    @classmethod
    def process_qr_payment(cls, merchant, wallet_id, amount, qr_code, reference=None, description=None):
        """Process a payment using QR code (merchant perspective)"""
        # Verify wallet exists and belongs to merchant
        try:
            wallet = Wallet.objects.get(wallet_id=wallet_id, merchant=merchant)
        except Wallet.DoesNotExist:
            raise WalletNotFoundError(f"Wallet with ID {wallet_id} not found")
        
        # Check wallet has sufficient balance
        if wallet.balance < Decimal(str(amount)):
            raise InsufficientFundsError(
                f"Insufficient funds in wallet. Available: {wallet.balance}, Required: {amount}"
            )
        
        # Create a reference if not provided
        if not reference:
            reference = f"QR_{str(uuid.uuid4())[:8]}"
        
        # Get payment method and status
        payment_method = cls.get_or_create_payment_method('qr_code', 'QR Code Payment')
        status = cls.get_transaction_status('completed')
        
        # Create transaction with atomic operation
        with transaction.atomic():
            # Debit the wallet
            wallet.balance -= Decimal(str(amount))
            wallet.save(update_fields=['balance'])
            
            # Create the transaction record
            transaction_obj = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='payment',
                status=status,
                payment_method=payment_method,
                reference=reference,
                description=description or 'QR Code Payment',
                merchant=merchant,
                customer=wallet.customer,
                payment_details={
                    'qr_code': qr_code[:10] + '...' if len(qr_code) > 10 else qr_code,
                    'payment_type': 'qr'
                }
            )
            
            logger.info(f"QR Payment processed: {transaction_obj.transaction_id} for amount {amount}")
            
            return transaction_obj
    
    @classmethod
    def process_eft_payment(cls, merchant, wallet_id, amount, bank_name, account_number, reference=None, description=None):
        """Process a payment using EFT (merchant perspective)"""
        # Verify wallet exists and belongs to merchant
        try:
            wallet = Wallet.objects.get(wallet_id=wallet_id, merchant=merchant)
        except Wallet.DoesNotExist:
            raise WalletNotFoundError(f"Wallet with ID {wallet_id} not found")
        
        # Check wallet has sufficient balance
        if wallet.balance < Decimal(str(amount)):
            raise InsufficientFundsError(
                f"Insufficient funds in wallet. Available: {wallet.balance}, Required: {amount}"
            )
        
        # Create a reference if not provided
        if not reference:
            reference = f"EFT_{str(uuid.uuid4())[:8]}"
        
        # Get payment method and status
        payment_method = cls.get_or_create_payment_method('eft', 'Electronic Fund Transfer')
        status = cls.get_transaction_status('completed')
        
        # Create transaction with atomic operation
        with transaction.atomic():
            # Debit the wallet
            wallet.balance -= Decimal(str(amount))
            wallet.save(update_fields=['balance'])
            
            # Create the transaction record
            transaction_obj = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='payment',
                status=status,
                payment_method=payment_method,
                reference=reference,
                description=description or 'EFT Payment',
                merchant=merchant,
                customer=wallet.customer,
                payment_details={
                    'bank_name': bank_name,
                    'account_number': f"*****{account_number[-4:]}" if len(account_number) > 4 else account_number,
                    'payment_type': 'eft'
                }
            )
            
            logger.info(f"EFT Payment processed: {transaction_obj.transaction_id} for amount {amount}")
            
            return transaction_obj
    
    @staticmethod
    def get_transaction_summary(merchant):
        """Get transaction summary statistics for a merchant"""
        all_transactions = Transaction.objects.filter(merchant=merchant)
        
        # Calculate total amounts by transaction type
        total_payments = all_transactions.filter(transaction_type='payment').count()
        total_deposits = all_transactions.filter(transaction_type='deposit').count()
        total_withdrawals = all_transactions.filter(transaction_type='withdrawal').count()
        
        # Calculate total amounts
        payment_volume = sum(t.amount for t in all_transactions.filter(transaction_type='payment'))
        deposit_volume = sum(t.amount for t in all_transactions.filter(transaction_type='deposit'))
        withdrawal_volume = sum(t.amount for t in all_transactions.filter(transaction_type='withdrawal'))
        
        # Get transaction counts by payment method
        payment_methods = {}
        for method in PaymentMethod.objects.all():
            count = all_transactions.filter(payment_method=method).count()
            if count > 0:
                payment_methods[method.code] = {
                    'name': method.name,
                    'count': count,
                    'volume': float(sum(t.amount for t in all_transactions.filter(payment_method=method)))
                }
        
        # Get recent transactions
        recent_transactions = all_transactions.order_by('-created_at')[:5]
        recent = [{
            'transaction_id': str(t.transaction_id),
            'amount': float(t.amount),
            'transaction_type': t.transaction_type,
            'status': t.status.code if t.status else 'unknown',
            'created_at': t.created_at.isoformat()
        } for t in recent_transactions]
        
        return {
            'total_transactions': all_transactions.count(),
            'transaction_counts': {
                'payments': total_payments,
                'deposits': total_deposits,
                'withdrawals': total_withdrawals
            },
            'transaction_volumes': {
                'payments': float(payment_volume),
                'deposits': float(deposit_volume),
                'withdrawals': float(withdrawal_volume),
                'total': float(payment_volume + deposit_volume + withdrawal_volume)
            },
            'payment_methods': payment_methods,
            'recent_transactions': recent
        }


class QRCodeService:
    """Service for QR code operations"""
    
    @staticmethod
    def create_qr_code(merchant_id: str, amount: Decimal, description: str = '', 
                      reference: str = '', expires_in_minutes: int = 15) -> QRCode:
        """Create a new QR code for payment"""
        try:
            merchant = Merchant.objects.get(id=merchant_id)
            
            # Create QR code object
            qr_code = QRCode.objects.create(
                merchant=merchant,
                amount=amount,
                description=description,
                reference=reference,
                expires_at=timezone.now() + timezone.timedelta(minutes=expires_in_minutes)
            )
            
            # Generate QR data
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            qr_data = {
                'token': qr_code.qr_token,
                'merchant_id': str(merchant.id),
                'merchant_name': merchant.business_name,
                'amount': str(amount),
                'description': description,
                'reference': reference,
                'expires_at': qr_code.expires_at.isoformat(),
                'payment_url': f"{base_url}/api/payments/qr/{qr_code.qr_token}/pay/"
            }
            
            qr_code.qr_data = json.dumps(qr_data)
            qr_code.save()
            
            logger.info(f"QR code created: {qr_code.qr_token} for merchant {merchant.business_name}")
            return qr_code
            
        except Merchant.DoesNotExist:
            raise ValueError("Merchant not found")
        except Exception as e:
            logger.error(f"Error creating QR code: {str(e)}")
            raise
    
    @staticmethod
    def generate_qr_image(qr_data: str):
        """Generate QR code image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white")
    
    @staticmethod
    def process_qr_payment(qr_code: QRCode, customer_phone: str, 
                          wallet_id: Optional[str] = None) -> Transaction:
        """Process payment using QR code"""
        try:
            # Get customer
            customer = Customer.objects.get(phone_number=customer_phone)
            
            # Get or create wallet
            if wallet_id:
                wallet = Wallet.objects.get(id=wallet_id, customer=customer)
            else:
                # Get customer's default wallet or create one
                wallet = Wallet.objects.filter(customer=customer).first()
                if not wallet:
                    raise ValueError("Customer has no wallet")
            
            # Check wallet balance
            total_amount = qr_code.amount + Decimal('2.00')  # Add transaction fee
            if wallet.balance < total_amount:
                raise ValueError("Insufficient wallet balance")
            
            # Create transaction
            with transaction.atomic():
                # Update QR code status
                qr_code.status = 'used'
                qr_code.customer = customer
                qr_code.save()
                
                # Create transaction record
                trans = Transaction.objects.create(
                    transaction_type='qr_payment',
                    amount=qr_code.amount,
                    fee=Decimal('2.00'),
                    net_amount=qr_code.amount,
                    from_wallet=wallet,
                    customer=customer,
                    merchant=qr_code.merchant,
                    status=TransactionService.get_transaction_status('completed'),
                    reference=qr_code.reference,
                    description=f"QR Payment: {qr_code.description}",
                    completed_at=timezone.now(),
                    metadata={
                        'qr_token': qr_code.qr_token,
                        'payment_method': 'qr_code'
                    }
                )
                
                # Update wallet balance
                wallet.balance -= total_amount
                wallet.save()
                
                # Link transaction to QR code
                qr_code.transaction = trans
                qr_code.save()
                
                logger.info(f"QR payment processed: {trans.transaction_id}")
                return trans
                
        except Customer.DoesNotExist:
            raise ValueError("Customer not found")
        except Wallet.DoesNotExist:
            raise ValueError("Wallet not found")
        except Exception as e:
            logger.error(f"Error processing QR payment: {str(e)}")
            raise


class EFTPaymentService:
    """Service for EFT payment operations"""
    
    BANK_CONFIGS = {
        'fnb': {
            'name': 'First National Bank',
            'api_url': 'https://api.fnb.co.bw/payments',
            'min_amount': Decimal('10.00'),
            'max_amount': Decimal('50000.00'),
            'fee_rate': Decimal('0.02')  # 2%
        },
        'standard': {
            'name': 'Standard Bank',
            'api_url': 'https://api.standardbank.co.bw/transfers',
            'min_amount': Decimal('10.00'),
            'max_amount': Decimal('100000.00'),
            'fee_rate': Decimal('0.015')  # 1.5%
        },
        'barclays': {
            'name': 'Barclays Bank',
            'api_url': 'https://api.barclays.co.bw/payments',
            'min_amount': Decimal('5.00'),
            'max_amount': Decimal('75000.00'),
            'fee_rate': Decimal('0.025')  # 2.5%
        },
        'nedbank': {
            'name': 'Nedbank',
            'api_url': 'https://api.nedbank.co.bw/payments',
            'min_amount': Decimal('10.00'),
            'max_amount': Decimal('75000.00'),
            'fee_rate': Decimal('0.02')  # 2%
        },
        'choppies': {
            'name': 'Choppies Bank',
            'api_url': 'https://api.choppiesbank.co.bw/payments',
            'min_amount': Decimal('5.00'),
            'max_amount': Decimal('25000.00'),
            'fee_rate': Decimal('0.03')  # 3%
        }
    }
    
    @staticmethod
    def initiate_eft_payment(customer_phone: str, wallet_id: str, amount: Decimal,
                           bank_code: str, account_number: str, reference: str = '') -> EFTPayment:
        """Initiate EFT payment for wallet top-up"""
        try:
            # Validate inputs
            customer = Customer.objects.get(phone_number=customer_phone)
            wallet = Wallet.objects.get(id=wallet_id, customer=customer)
            
            if bank_code not in EFTPaymentService.BANK_CONFIGS:
                raise ValueError("Unsupported bank")
            
            bank_config = EFTPaymentService.BANK_CONFIGS[bank_code]
            
            if amount < bank_config['min_amount'] or amount > bank_config['max_amount']:
                raise ValueError(f"Amount must be between {bank_config['min_amount']} and {bank_config['max_amount']}")
            
            # Create EFT payment record
            eft_payment = EFTPayment.objects.create(
                customer=customer,
                wallet=wallet,
                amount=amount,
                bank_code=bank_code,
                account_number=account_number,
                reference=reference or f"TOPUP-{timezone.now().strftime('%Y%m%d-%H%M%S')}",
                status='pending'
            )
            
            # Process with bank API (mock implementation)
            try:
                bank_response = EFTPaymentService._process_with_bank(eft_payment, bank_config)
                
                eft_payment.external_reference = bank_response.get('reference')
                eft_payment.response_data = bank_response
                eft_payment.status = 'processing'
                eft_payment.processed_at = timezone.now()
                eft_payment.save()
                
                logger.info(f"EFT payment initiated: {eft_payment.id}")
                
            except Exception as e:
                eft_payment.status = 'failed'
                eft_payment.response_data = {'error': str(e)}
                eft_payment.save()
                logger.error(f"EFT payment failed: {eft_payment.id} - {str(e)}")
                raise
            
            return eft_payment
            
        except (Customer.DoesNotExist, Wallet.DoesNotExist):
            raise ValueError("Customer or wallet not found")
        except Exception as e:
            logger.error(f"Error initiating EFT payment: {str(e)}")
            raise
    
    @staticmethod
    def _process_with_bank(eft_payment: EFTPayment, bank_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with bank API (mock implementation)"""
        # In production, this would make actual API calls to bank systems
        # For demo purposes, we'll simulate different scenarios
        
        import random
        import time
        
        # Simulate processing delay
        time.sleep(1)
        
        # Mock response scenarios
        scenarios = ['success', 'pending', 'failed']
        weights = [0.8, 0.15, 0.05]  # 80% success, 15% pending, 5% failed
        outcome = random.choices(scenarios, weights=weights)[0]
        
        if outcome == 'success':
            return {
                'status': 'completed',
                'reference': f"BNK-{random.randint(100000, 999999)}",
                'transaction_id': f"TXN-{random.randint(1000000, 9999999)}",
                'timestamp': timezone.now().isoformat(),
                'fee': str(eft_payment.amount * bank_config['fee_rate'])
            }
        elif outcome == 'pending':
            return {
                'status': 'pending',
                'reference': f"BNK-{random.randint(100000, 999999)}",
                'message': 'Payment is being processed',
                'timestamp': timezone.now().isoformat()
            }
        else:
            raise Exception("Bank declined the transaction")
    
    @staticmethod
    def process_webhook(external_reference: str, webhook_data: Dict[str, Any]) -> bool:
        """Process webhook from bank systems"""
        try:
            eft_payment = EFTPayment.objects.get(external_reference=external_reference)
            
            status_mapping = {
                'completed': 'completed',
                'success': 'completed',
                'failed': 'failed',
                'declined': 'failed',
                'cancelled': 'cancelled'
            }
            
            new_status = status_mapping.get(webhook_data.get('status'), 'failed')
            
            with transaction.atomic():
                eft_payment.status = new_status
                eft_payment.response_data.update(webhook_data)
                
                if new_status == 'completed':
                    eft_payment.completed_at = timezone.now()
                    
                    # Create successful transaction and update wallet
                    trans = Transaction.objects.create(
                        transaction_type='eft_topup',
                        amount=eft_payment.amount,
                        fee=Decimal(webhook_data.get('fee', '0.00')),
                        to_wallet=eft_payment.wallet,
                        customer=eft_payment.customer,
                        status=TransactionService.get_transaction_status('completed'),
                        reference=eft_payment.reference,
                        description=f"EFT Top-up from {eft_payment.bank_code}",
                        completed_at=timezone.now(),
                        metadata={
                            'bank_code': eft_payment.bank_code,
                            'external_reference': external_reference,
                            'payment_method': 'eft'
                        }
                    )
                    
                    # Update wallet balance
                    net_amount = eft_payment.amount - Decimal(webhook_data.get('fee', '0.00'))
                    eft_payment.wallet.balance += net_amount
                    eft_payment.wallet.save()
                    
                    # Link transaction
                    eft_payment.transaction = trans
                    
                eft_payment.save()
                
                logger.info(f"EFT webhook processed: {external_reference} - {new_status}")
                return True
                
        except EFTPayment.DoesNotExist:
            logger.error(f"EFT payment not found for reference: {external_reference}")
            return False
        except Exception as e:
            logger.error(f"Error processing EFT webhook: {str(e)}")
            raise
    
    @staticmethod
    def check_payment_status(eft_payment_id: str) -> EFTPayment:
        """Check current status of EFT payment"""
        try:
            eft_payment = EFTPayment.objects.select_related('customer', 'wallet', 'transaction').get(id=eft_payment_id)
            
            # If still processing, check with bank (mock implementation)
            if eft_payment.status == 'processing':
                # In production, this would query the bank API
                # For demo, we'll randomly update some pending payments
                import random
                if random.random() < 0.3:  # 30% chance to complete
                    EFTPaymentService.process_webhook(
                        eft_payment.external_reference,
                        {
                            'status': 'completed',
                            'fee': '5.00',
                            'timestamp': timezone.now().isoformat()
                        }
                    )
                    eft_payment.refresh_from_db()
            
            return eft_payment
            
        except EFTPayment.DoesNotExist:
            raise ValueError("EFT payment not found")


class PaymentAnalyticsService:
    """Service for payment analytics and reporting"""
    
    @staticmethod
    def get_payment_summary(date_from=None, date_to=None, merchant_id=None):
        """Get payment summary statistics"""
        queryset = Transaction.objects.all()
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)
        
        from django.db.models import Sum, Count, Q
        
        summary = queryset.aggregate(
            total_amount=Sum('amount'),
            total_transactions=Count('transaction_id'),
            successful_payments=Count('transaction_id', filter=Q(status__code='completed')),
            failed_payments=Count('transaction_id', filter=Q(status__code='failed')),
            pending_payments=Count('transaction_id', filter=Q(status__code='pending'))
        )
        
        return summary