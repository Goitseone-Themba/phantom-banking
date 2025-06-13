import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from phantom_apps.transactions.models import PaymentMethod, TransactionStatus, QRCode, EFTPayment, Transaction
from phantom_apps.merchants.models import Merchant
from phantom_apps.customers.models import Customer
from phantom_apps.wallets.models import Wallet


class Command(BaseCommand):
    help = 'Setup payment system with initial data and test scenarios'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create comprehensive test data',
        )
        parser.add_argument(
            '--reset-data',
            action='store_true',
            help='Reset all payment-related data (DESTRUCTIVE)',
        )
        parser.add_argument(
            '--create-sample-transactions',
            type=int,
            default=0,
            help='Number of sample transactions to create',
        )
        parser.add_argument(
            '--setup-banks',
            action='store_true',
            help='Setup bank configurations and test webhooks',
        )
    
    def handle(self, *args, **options):
        if options['reset_data']:
            self.reset_data()
        
        self.setup_payment_methods()
        self.setup_transaction_statuses()
        
        if options['create_test_data']:
            self.create_test_data()
        
        if options['create_sample_transactions'] > 0:
            self.create_sample_transactions(options['create_sample_transactions'])
        
        if options['setup_banks']:
            self.setup_bank_configurations()
        
        self.stdout.write(
            self.style.SUCCESS('Payment system setup completed successfully!')
        )
    
    def reset_data(self):
        """Reset all payment-related data"""
        self.stdout.write(self.style.WARNING('Resetting payment data...'))
        
        with transaction.atomic():
            Transaction.objects.all().delete()
            QRCode.objects.all().delete()
            EFTPayment.objects.all().delete()
            # Don't delete PaymentMethod and TransactionStatus as they're reference data
        
        self.stdout.write(self.style.SUCCESS('Payment data reset complete'))
    
    def setup_payment_methods(self):
        """Setup standard payment methods"""
        self.stdout.write('Setting up payment methods...')
        
        payment_methods = [
            ('qr_code', 'QR Code Payment', 'Payment via QR code scanning'),
            ('eft', 'Electronic Fund Transfer', 'Bank-to-bank electronic transfer'),
            ('mobile_money', 'Mobile Money', 'Mobile money transfer'),
            ('bank_transfer', 'Bank Transfer', 'Direct bank transfer'),
            ('card', 'Card Payment', 'Credit/Debit card payment'),
            ('cash', 'Cash Payment', 'Cash payment'),
            ('wallet', 'Wallet Transfer', 'Internal wallet transfer'),
        ]
        
        for code, name, description in payment_methods:
            method, created = PaymentMethod.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'  Created payment method: {name}')
            else:
                self.stdout.write(f'  Payment method exists: {name}')
    
    def setup_transaction_statuses(self):
        """Setup standard transaction statuses"""
        self.stdout.write('Setting up transaction statuses...')
        
        statuses = [
            ('pending', 'Pending', 'Transaction is pending processing'),
            ('processing', 'Processing', 'Transaction is being processed'),
            ('completed', 'Completed', 'Transaction completed successfully'),
            ('failed', 'Failed', 'Transaction failed'),
            ('cancelled', 'Cancelled', 'Transaction was cancelled'),
            ('refunded', 'Refunded', 'Transaction was refunded'),
            ('disputed', 'Disputed', 'Transaction is under dispute'),
            ('on_hold', 'On Hold', 'Transaction is on hold'),
        ]
        
        for code, name, description in statuses:
            status, created = TransactionStatus.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description
                }
            )
            
            if created:
                self.stdout.write(f'  Created status: {name}')
            else:
                self.stdout.write(f'  Status exists: {name}')
    
    def create_test_data(self):
        """Create comprehensive test data"""
        self.stdout.write('Creating test data...')
        
        with transaction.atomic():
            # Create test users and merchants
            self.create_test_merchants()
            
            # Create test customers and wallets
            self.create_test_customers()
            
            # Create test QR codes
            self.create_test_qr_codes()
            
            # Create test EFT payments
            self.create_test_eft_payments()
    
    def create_test_merchants(self):
        """Create test merchants"""
        self.stdout.write('  Creating test merchants...')
        
        merchants_data = [
            {
                'username': 'testmerchant1',
                'business_name': 'Café Delights',
                'contact_email': 'admin@cafedelights.bw',
                'phone_number': '+26771000001',
                'description': 'Premium coffee and pastries'
            },
            {
                'username': 'testmerchant2', 
                'business_name': 'TechStore BW',
                'contact_email': 'sales@techstore.bw',
                'phone_number': '+26771000002',
                'description': 'Electronics and gadgets'
            },
            {
                'username': 'testmerchant3',
                'business_name': 'Fashion Hub',
                'contact_email': 'info@fashionhub.bw',
                'phone_number': '+26771000003',
                'description': 'Trendy clothing and accessories'
            }
        ]
        
        for merchant_data in merchants_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=merchant_data['username'],
                defaults={
                    'email': merchant_data['contact_email'],
                    'first_name': merchant_data['business_name'].split()[0],
                    'last_name': 'Admin'
                }
            )
            
            if created:
                user.set_password('testpassword123')
                user.save()
            
            # Create merchant
            merchant, created = Merchant.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': merchant_data['business_name'],
                    'contact_email': merchant_data['contact_email'],
                    'phone_number': merchant_data['phone_number'],
                    'description': merchant_data.get('description', '')
                }
            )
            
            if created:
                self.stdout.write(f'    Created merchant: {merchant.business_name}')
            
            # Store reference for later use
            setattr(self, f'merchant_{merchant_data["username"]}', merchant)
    
    def create_test_customers(self):
        """Create test customers and wallets"""
        self.stdout.write('  Creating test customers and wallets...')
        
        customers_data = [
            {
                'phone_number': '71000001',
                'full_name': 'John Doe',
                'email': 'john.doe@email.com',
                'wallet_balance': '1500.00'
            },
            {
                'phone_number': '71000002',
                'full_name': 'Jane Smith',
                'email': 'jane.smith@email.com', 
                'wallet_balance': '2000.00'
            },
            {
                'phone_number': '71000003',
                'full_name': 'Mike Johnson',
                'email': 'mike.johnson@email.com',
                'wallet_balance': '750.00'
            },
            {
                'phone_number': '71000004',
                'full_name': 'Sarah Wilson',
                'email': 'sarah.wilson@email.com',
                'wallet_balance': '3000.00'
            }
        ]
        
        merchants = [self.merchant_testmerchant1, self.merchant_testmerchant2, self.merchant_testmerchant3]
        
        for i, customer_data in enumerate(customers_data):
            # Create customer
            customer, created = Customer.objects.get_or_create(
                phone_number=customer_data['phone_number'],
                defaults={
                    'full_name': customer_data['full_name'],
                    'email': customer_data['email']
                }
            )
            
            if created:
                self.stdout.write(f'    Created customer: {customer.full_name}')
            
            # Create wallet for each merchant
            for merchant in merchants:
                wallet, created = Wallet.objects.get_or_create(
                    customer=customer,
                    merchant=merchant,
                    defaults={
                        'balance': Decimal(customer_data['wallet_balance']),
                        'currency': 'BWP',
                        'status': 'active'
                    }
                )
                
                if created:
                    self.stdout.write(f'      Created wallet: {customer.full_name} - {merchant.business_name}')
            
            # Store reference for later use
            setattr(self, f'customer_{i+1}', customer)
    
    def create_test_qr_codes(self):
        """Create test QR codes"""
        self.stdout.write('  Creating test QR codes...')
        
        from phantom_apps.transactions.services import QRCodeService
        
        qr_codes_data = [
            {
                'merchant': self.merchant_testmerchant1,
                'amount': '25.50',
                'description': 'Coffee and muffin',
                'expires_in_minutes': 30
            },
            {
                'merchant': self.merchant_testmerchant2,
                'amount': '499.99',
                'description': 'Bluetooth headphones',
                'expires_in_minutes': 60
            },
            {
                'merchant': self.merchant_testmerchant3,
                'amount': '89.00',
                'description': 'T-shirt',
                'expires_in_minutes': 15
            },
            {
                'merchant': self.merchant_testmerchant1,
                'amount': '15.00',
                'description': 'Espresso shot',
                'expires_in_minutes': 10
            }
        ]
        
        for qr_data in qr_codes_data:
            qr_code = QRCodeService.create_qr_code(
                merchant_id=str(qr_data['merchant'].id),
                amount=Decimal(qr_data['amount']),
                description=qr_data['description'],
                expires_in_minutes=qr_data['expires_in_minutes']
            )
            
            self.stdout.write(f'    Created QR code: {qr_code.qr_token} - P{qr_code.amount}')
    
    def create_test_eft_payments(self):
        """Create test EFT payments"""
        self.stdout.write('  Creating test EFT payments...')
        
        eft_payments_data = [
            {
                'customer': self.customer_1,
                'amount': '500.00',
                'bank_code': 'fnb',
                'account_number': '1234567890',
                'reference': 'TOPUP-001',
                'status': 'completed'
            },
            {
                'customer': self.customer_2,
                'amount': '1000.00',
                'bank_code': 'standard',
                'account_number': '9876543210',
                'reference': 'TOPUP-002',
                'status': 'processing'
            },
            {
                'customer': self.customer_3,
                'amount': '250.00',
                'bank_code': 'barclays',
                'account_number': '5555666677',
                'reference': 'TOPUP-003',
                'status': 'failed'
            }
        ]
        
        # Get first wallet for each customer
        for eft_data in eft_payments_data:
            wallet = Wallet.objects.filter(customer=eft_data['customer']).first()
            
            if wallet:
                eft_payment = EFTPayment.objects.create(
                    customer=eft_data['customer'],
                    wallet=wallet,
                    amount=Decimal(eft_data['amount']),
                    bank_code=eft_data['bank_code'],
                    account_number=eft_data['account_number'],
                    reference=eft_data['reference'],
                    status=eft_data['status'],
                    external_reference=f"BNK-{uuid.uuid4().hex[:8].upper()}"
                )
                
                if eft_data['status'] == 'completed':
                    eft_payment.completed_at = timezone.now()
                    eft_payment.save()
                
                self.stdout.write(f'    Created EFT payment: {eft_payment.reference} - P{eft_payment.amount}')
    
    def create_sample_transactions(self, count):
        """Create sample transactions for testing"""
        self.stdout.write(f'Creating {count} sample transactions...')
        
        import random
        from phantom_apps.transactions.services import QRCodeService
        
        # Get test data
        customers = [self.customer_1, self.customer_2, self.customer_3, self.customer_4]
        merchants = [self.merchant_testmerchant1, self.merchant_testmerchant2, self.merchant_testmerchant3]
        transaction_types = ['qr_payment', 'eft_topup', 'wallet_transfer']
        amounts = ['10.00', '25.50', '50.00', '100.00', '250.00', '500.00']
        
        completed_status = TransactionStatus.objects.get(code='completed')
        qr_method = PaymentMethod.objects.get(code='qr_code')
        
        with transaction.atomic():
            for i in range(count):
                customer = random.choice(customers)
                merchant = random.choice(merchants)
                wallet = Wallet.objects.filter(customer=customer, merchant=merchant).first()
                
                if wallet and wallet.balance > Decimal('100.00'):
                    # Create QR payment transaction
                    amount = Decimal(random.choice(amounts))
                    
                    if wallet.balance >= amount:
                        trans = Transaction.objects.create(
                            transaction_type='qr_payment',
                            amount=amount,
                            fee=Decimal('2.00'),
                            from_wallet=wallet,
                            customer=customer,
                            merchant=merchant,
                            status=completed_status,
                            payment_method=qr_method,
                            reference=f'SAMPLE-{i+1:04d}',
                            description=f'Sample transaction {i+1}',
                            completed_at=timezone.now(),
                            metadata={'sample': True}
                        )
                        
                        # Update wallet balance
                        wallet.balance -= (amount + Decimal('2.00'))
                        wallet.save()
                        
                        if i % 10 == 0:
                            self.stdout.write(f'  Created {i+1} transactions...')
        
        self.stdout.write(f'Created {count} sample transactions')
    
    def setup_bank_configurations(self):
        """Setup bank configurations and test webhook URLs"""
        self.stdout.write('Setting up bank configurations...')
        
        bank_configs = {
            'fnb': {
                'name': 'First National Bank',
                'webhook_url': '/api/transactions/eft/webhook/',
                'test_credentials': 'test_fnb_api_key',
                'fee_rate': '2.0%'
            },
            'standard': {
                'name': 'Standard Bank',
                'webhook_url': '/api/transactions/eft/webhook/',
                'test_credentials': 'test_standard_api_key',
                'fee_rate': '1.5%'
            },
            'barclays': {
                'name': 'Barclays Bank',
                'webhook_url': '/api/transactions/eft/webhook/',
                'test_credentials': 'test_barclays_api_key',
                'fee_rate': '2.5%'
            },
            'nedbank': {
                'name': 'Nedbank',
                'webhook_url': '/api/transactions/eft/webhook/',
                'test_credentials': 'test_nedbank_api_key',
                'fee_rate': '2.0%'
            },
            'choppies': {
                'name': 'Choppies Bank',
                'webhook_url': '/api/transactions/eft/webhook/',
                'test_credentials': 'test_choppies_api_key',
                'fee_rate': '3.0%'
            }
        }
        
        for bank_code, config in bank_configs.items():
            self.stdout.write(f'  {config["name"]} ({bank_code}):')
            self.stdout.write(f'    Webhook URL: {config["webhook_url"]}')
            self.stdout.write(f'    Fee Rate: {config["fee_rate"]}')
        
        self.stdout.write('\nTest webhook endpoints:')
        self.stdout.write('  POST /api/transactions/eft/webhook/')
        self.stdout.write('  POST /api/webhooks/eft/')
        self.stdout.write('  POST /api/webhooks/eft/{bank_code}/')
    
    def display_summary(self):
        """Display setup summary"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('PAYMENT SYSTEM SETUP SUMMARY')
        self.stdout.write('='*50)
        
        # Count records
        payment_methods_count = PaymentMethod.objects.count()
        statuses_count = TransactionStatus.objects.count()
        merchants_count = Merchant.objects.count()
        customers_count = Customer.objects.count()
        wallets_count = Wallet.objects.count()
        qr_codes_count = QRCode.objects.count()
        eft_payments_count = EFTPayment.objects.count()
        transactions_count = Transaction.objects.count()
        
        self.stdout.write(f'Payment Methods: {payment_methods_count}')
        self.stdout.write(f'Transaction Statuses: {statuses_count}')
        self.stdout.write(f'Merchants: {merchants_count}')
        self.stdout.write(f'Customers: {customers_count}')
        self.stdout.write(f'Wallets: {wallets_count}')
        self.stdout.write(f'QR Codes: {qr_codes_count}')
        self.stdout.write(f'EFT Payments: {eft_payments_count}')
        self.stdout.write(f'Transactions: {transactions_count}')
        
        self.stdout.write('\nAPI Endpoints:')
        self.stdout.write('  QR Codes: /api/transactions/qr/')
        self.stdout.write('  EFT Payments: /api/transactions/eft/')
        self.stdout.write('  Transactions: /api/transactions/transactions/')
        self.stdout.write('  Analytics: /api/transactions/analytics/')
        
        self.stdout.write('\nTest Users:')
        self.stdout.write('  testmerchant1 / testpassword123')
        self.stdout.write('  testmerchant2 / testpassword123')
        self.stdout.write('  testmerchant3 / testpassword123')
        
        self.stdout.write('\nTest Customers:')
        self.stdout.write('  71000001 - John Doe')
        self.stdout.write('  71000002 - Jane Smith')
        self.stdout.write('  71000003 - Mike Johnson')
        self.stdout.write('  71000004 - Sarah Wilson')
        
        self.stdout.write('\n' + '='*50)