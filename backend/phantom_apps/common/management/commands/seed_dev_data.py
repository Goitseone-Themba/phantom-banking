"""
Development Data Seeding Script for Phantom Banking

This script creates comprehensive dummy data for development including:
- Multiple merchants with different business types
- Customers with various profiles and statuses
- Wallets with different balances and verification levels
- KYC records with different statuses
- Transaction history
- Payment methods and transaction statuses
"""

import random
import secrets
import string
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction as db_transaction

from phantom_apps.merchants.models import Merchant, APICredential
from phantom_apps.customers.models import Customer
from phantom_apps.wallets.models import Wallet
from phantom_apps.kyc.models import KYCRecord, KYCDocument, KYCEvent
from phantom_apps.transactions.models import (
    PaymentMethod, TransactionStatus, Transaction, QRCode, EFTPayment
)


class Command(BaseCommand):
    help = 'Seed the database with comprehensive development data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
        parser.add_argument(
            '--merchants',
            type=int,
            default=8,
            help='Number of merchants to create'
        )
        parser.add_argument(
            '--customers-per-merchant',
            type=int,
            default=15,
            help='Average number of customers per merchant'
        )
        parser.add_argument(
            '--transactions-per-customer',
            type=int,
            default=10,
            help='Average number of transactions per customer'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️  Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('🌱 Starting data seeding...')
        
        with db_transaction.atomic():
            # Create lookup data first
            payment_methods = self.create_payment_methods()
            transaction_statuses = self.create_transaction_statuses()
            
            # Create core business data
            merchants = self.create_merchants(options['merchants'])
            customers = self.create_customers(merchants, options['customers_per_merchant'])
            wallets = self.create_wallets(customers)
            
            # Create KYC data
            kyc_records = self.create_kyc_records(customers)
            
            # Create transaction data
            self.create_transactions(
                customers, 
                payment_methods, 
                transaction_statuses,
                options['transactions_per_customer']
            )
            
            # Create QR codes and EFT payments
            self.create_qr_codes(merchants)
            self.create_eft_payments(customers)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully seeded database with comprehensive development data!\n'
                f'   📊 Summary:\n'
                f'   - {len(merchants)} merchants\n'
                f'   - {len(customers)} customers\n'
                f'   - {len(wallets)} wallets\n'
                f'   - {len(kyc_records)} KYC records\n'
                f'   - Payment methods and transaction statuses\n'
                f'   - QR codes and EFT payments\n'
                f'   - Transaction history'
            )
        )
    
    def clear_data(self):
        """Clear existing data"""
        models_to_clear = [
            Transaction, QRCode, EFTPayment,
            KYCEvent, KYCDocument, KYCRecord,
            Wallet, Customer,
            APICredential, Merchant,
            PaymentMethod, TransactionStatus
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'   Cleared {count} {model.__name__} records')
        
        # Clear users (except superusers)
        user_count = User.objects.filter(is_superuser=False).count()
        if user_count > 0:
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(f'   Cleared {user_count} User records')
    
    def create_payment_methods(self):
        """Create payment method lookup data"""
        methods = [
            ('qr_code', 'QR Code Payment', 'Pay using QR code scan'),
            ('eft', 'Electronic Funds Transfer', 'Bank transfer payment'),
            ('wallet', 'Phantom Wallet', 'Internal wallet payment'),
            ('mobile_money', 'Mobile Money', 'Orange Money, Mascom MyZaka'),
            ('bank_card', 'Bank Card', 'Debit/Credit card payment'),
        ]
        
        payment_methods = []
        for code, name, description in methods:
            method, created = PaymentMethod.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': description}
            )
            payment_methods.append(method)
        
        self.stdout.write(f'   Created {len(payment_methods)} payment methods')
        return payment_methods
    
    def create_transaction_statuses(self):
        """Create transaction status lookup data"""
        statuses = [
            ('pending', 'Pending', 'Transaction is pending processing'),
            ('processing', 'Processing', 'Transaction is being processed'),
            ('completed', 'Completed', 'Transaction completed successfully'),
            ('failed', 'Failed', 'Transaction failed'),
            ('cancelled', 'Cancelled', 'Transaction was cancelled'),
            ('refunded', 'Refunded', 'Transaction was refunded'),
            ('expired', 'Expired', 'Transaction expired'),
        ]
        
        transaction_statuses = []
        for code, name, description in statuses:
            status, created = TransactionStatus.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': description}
            )
            transaction_statuses.append(status)
        
        self.stdout.write(f'   Created {len(transaction_statuses)} transaction statuses')
        return transaction_statuses
    
    def create_merchants(self, count):
        """Create merchant accounts with different business types"""
        business_types = [
            ('Retail Store', 'General retail and consumer goods'),
            ('Restaurant', 'Food service and dining'),
            ('Pharmacy', 'Medical supplies and prescriptions'),
            ('Gas Station', 'Fuel and convenience store'),
            ('Supermarket', 'Grocery and household items'),
            ('Electronics Store', 'Consumer electronics and gadgets'),
            ('Clothing Store', 'Fashion and apparel'),
            ('Hardware Store', 'Tools and construction materials'),
        ]
        
        merchants = []
        for i in range(count):
            business_type, description = business_types[i % len(business_types)]
            
            # Create user account
            username = f'merchant_{i+1}_{business_type.lower().replace(" ", "_")}'
            user = User.objects.create_user(
                username=username,
                email=f'{username}@phantombanking.dev',
                password='dev_password_123',
                first_name=business_type,
                last_name='Owner'
            )
            
            # Create merchant
            merchant = Merchant.objects.create(
                user=user,
                business_name=f'{business_type} #{i+1}',
                fnb_account_number=f'FNB{1000000 + i:07d}',
                contact_email=f'{username}@phantombanking.dev',
                phone_number=f'+26777{100000 + i:06d}',
                business_registration=f'BW{2024000 + i:06d}',
                api_key=self.generate_api_key(),
                api_secret_hash=self.generate_secret_hash(),
                commission_rate=Decimal(str(random.uniform(0.5, 2.5))),
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            
            # Create API credentials
            APICredential.objects.create(
                merchant=merchant,
                api_key=self.generate_api_key(),
                api_secret_hash=self.generate_secret_hash(),
                permissions=['read', 'write', 'admin'] if random.random() > 0.3 else ['read', 'write'],
                is_active=True
            )
            
            merchants.append(merchant)
        
        self.stdout.write(f'   Created {len(merchants)} merchants')
        return merchants
    
    def create_customers(self, merchants, avg_customers_per_merchant):
        """Create customers for each merchant"""
        first_names = [
            'Thabo', 'Mpho', 'Keabetswe', 'Tshepo', 'Nomsa', 'Refilwe',
            'Kagiso', 'Tebogo', 'Mmabatho', 'Kealeboga', 'Boitumelo', 'Masego',
            'Gaone', 'Neo', 'Phenyo', 'Kutlwano', 'Onalenna', 'Itumeleng',
            'Lerato', 'Tumelo', 'Gomolemo', 'Oratile', 'Keneilwe', 'Thato'
        ]
        
        last_names = [
            'Mothibi', 'Sekgoma', 'Khama', 'Sebogo', 'Tshosa', 'Molefe',
            'Mogapi', 'Setlhare', 'Moatlhodi', 'Kgosana', 'Seeletso', 'Kebaabetswe',
            'Mogorosi', 'Modise', 'Gaolathe', 'Mmualefe', 'Kgalemang', 'Moremi',
            'Masire', 'Mogae', 'Ian', 'Ramsay', 'Tafa', 'Segwaba'
        ]
        
        customers = []
        customer_id = 1
        
        for merchant in merchants:
            # Vary the number of customers per merchant
            num_customers = random.randint(
                max(1, avg_customers_per_merchant - 5),
                avg_customers_per_merchant + 5
            )
            
            for i in range(num_customers):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                customer = Customer.objects.create(
                    merchant=merchant,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=f'+26771{200000 + customer_id:06d}',
                    email=f'{first_name.lower()}.{last_name.lower()}@example.com' if random.random() > 0.2 else None,
                    identity_number=f'ID{customer_id:08d}' if random.random() > 0.3 else None,
                    status=random.choice(['active', 'active', 'active', 'inactive', 'suspended']),
                    is_verified=random.choice([True, True, False]),
                    preferred_language=random.choice(['en', 'tn', 'en']),  # English and Setswana
                    nationality=random.choice(['BW', 'BW', 'BW', 'ZA', 'ZW', 'NA'])  # Mostly Botswana
                )
                
                customers.append(customer)
                customer_id += 1
        
        self.stdout.write(f'   Created {len(customers)} customers')
        return customers
    
    def create_wallets(self, customers):
        """Create wallets for customers with varying balances and types"""
        wallets = []
        
        for customer in customers:
            # Determine wallet type based on verification status
            if customer.is_verified:
                wallet_type = random.choice(['verified', 'premium', 'verified'])
                daily_limit = random.choice([50000, 75000, 100000])
                monthly_limit = random.choice([200000, 500000, 1000000])
            else:
                wallet_type = 'basic'
                daily_limit = random.choice([10000, 15000, 20000])
                monthly_limit = random.choice([50000, 75000, 100000])
            
            # Generate realistic balance
            if customer.status == 'active':
                balance_ranges = {
                    'basic': (0, 5000),
                    'verified': (100, 25000),
                    'premium': (500, 100000)
                }
                min_bal, max_bal = balance_ranges[wallet_type]
                balance = Decimal(str(random.uniform(min_bal, max_bal))).quantize(Decimal('0.01'))
            else:
                balance = Decimal('0.00')
            
            wallet = Wallet.objects.create(
                customer=customer,
                merchant=customer.merchant,
                balance=balance,
                currency='BWP',
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
                status=customer.status,
                is_frozen=random.choice([False, False, False, True]) if customer.status == 'active' else True,
                is_kyc_verified=customer.is_verified,
                wallet_type=wallet_type,
                upgraded_at=timezone.now() - timedelta(days=random.randint(1, 365)) if wallet_type != 'basic' else None
            )
            
            wallets.append(wallet)
        
        self.stdout.write(f'   Created {len(wallets)} wallets')
        return wallets
    
    def create_kyc_records(self, customers):
        """Create KYC records with different statuses"""
        kyc_records = []
        
        # Create some admin users for KYC review
        admin_users = []
        for i in range(3):
            admin_user, created = User.objects.get_or_create(
                username=f'kyc_admin_{i+1}',
                defaults={
                    'email': f'kyc_admin_{i+1}@phantombanking.dev',
                    'first_name': f'KYC Admin {i+1}',
                    'is_staff': True
                }
            )
            admin_users.append(admin_user)
        
        nationalities = ['BWA', 'ZAF', 'ZWE', 'NAM', 'ZMB']
        document_types = ['passport', 'id_card', 'driving_license']
        cities = ['Gaborone', 'Francistown', 'Molepolole', 'Selebi-Phikwe', 'Maun', 'Serowe', 'Kanye']
        
        for customer in customers:
            # Create user account for KYC (if customer doesn't have one)
            user, created = User.objects.get_or_create(
                username=f'customer_{customer.customer_id}',
                defaults={
                    'email': customer.email or f'customer_{customer.customer_id}@example.com',
                    'first_name': customer.first_name,
                    'last_name': customer.last_name
                }
            )
            
            # Determine KYC status based on customer verification
            if customer.is_verified:
                status = random.choice([
                    KYCRecord.Status.APPROVED,
                    KYCRecord.Status.APPROVED,
                    KYCRecord.Status.APPROVED
                ])
                verification_level = random.choice([
                    KYCRecord.VerificationLevel.ENHANCED,
                    KYCRecord.VerificationLevel.PREMIUM
                ])
                risk_score = Decimal(str(random.uniform(10, 40)))
                risk_level = 'low'
            else:
                status = random.choice([
                    KYCRecord.Status.PENDING,
                    KYCRecord.Status.IN_PROGRESS,
                    KYCRecord.Status.REJECTED,
                    KYCRecord.Status.RESUBMISSION_REQUESTED
                ])
                verification_level = KYCRecord.VerificationLevel.BASIC
                risk_score = Decimal(str(random.uniform(30, 80)))
                risk_level = random.choice(['medium', 'high'])
            
            # Create KYC record
            kyc_record = KYCRecord.objects.create(
                user=user,
                status=status,
                verification_level=verification_level,
                first_name=customer.first_name,
                last_name=customer.last_name,
                date_of_birth=datetime(1980, 1, 1).date() + timedelta(days=random.randint(0, 15000)),
                nationality=random.choice(nationalities),
                document_type=random.choice(document_types),
                document_number=f'DOC{random.randint(100000, 999999)}',
                address_line_1=f'{random.randint(1, 999)} {random.choice(["Main", "Church", "Independence", "Nelson Mandela"])} Street',
                address_line_2=f'Unit {random.randint(1, 50)}' if random.random() > 0.7 else '',
                city=random.choice(cities),
                state_province='Gaborone' if random.choice(cities) == 'Gaborone' else 'Other',
                postal_code=f'{random.randint(1000, 9999)}',
                country='BWA',
                risk_score=risk_score,
                risk_level=risk_level,
                reviewed_by=random.choice(admin_users) if status in [KYCRecord.Status.APPROVED, KYCRecord.Status.REJECTED] else None,
                verified_at=timezone.now() - timedelta(days=random.randint(1, 180)) if status == KYCRecord.Status.APPROVED else None,
                expires_at=timezone.now() + timedelta(days=365) if status == KYCRecord.Status.APPROVED else None,
                veriff_session_id=f'session_{random.randint(100000, 999999)}' if random.random() > 0.3 else None,
                veriff_decision='approved' if status == KYCRecord.Status.APPROVED else None
            )
            
            # Create KYC events
            events = [
                (KYCEvent.EventType.SESSION_CREATED, 'KYC verification session initiated'),
                (KYCEvent.EventType.DOCUMENTS_UPLOADED, 'Identity documents uploaded'),
                (KYCEvent.EventType.VERIFICATION_STARTED, 'Document verification started'),
            ]
            
            if status == KYCRecord.Status.APPROVED:
                events.extend([
                    (KYCEvent.EventType.VERIFICATION_COMPLETED, 'Document verification completed'),
                    (KYCEvent.EventType.APPROVED, 'KYC verification approved')
                ])
            elif status == KYCRecord.Status.REJECTED:
                events.append((KYCEvent.EventType.REJECTED, 'KYC verification rejected'))
            
            for event_type, description in events:
                KYCEvent.objects.create(
                    kyc_record=kyc_record,
                    event_type=event_type,
                    description=description,
                    created_by=random.choice(admin_users) if random.random() > 0.5 else None,
                    metadata={'automated': True}
                )
            
            # Create documents
            if random.random() > 0.2:  # 80% have documents
                for doc_type in ['passport', 'proof_of_address']:
                    KYCDocument.objects.create(
                        kyc_record=kyc_record,
                        document_type=doc_type,
                        file_url=f'https://dev-storage.phantombanking.bw/kyc/{kyc_record.id}/{doc_type}.jpg',
                        file_name=f'{doc_type}_{kyc_record.id}.jpg',
                        verified=status == KYCRecord.Status.APPROVED
                    )
            
            kyc_records.append(kyc_record)
        
        self.stdout.write(f'   Created {len(kyc_records)} KYC records with events and documents')
        return kyc_records
    
    def create_transactions(self, customers, payment_methods, transaction_statuses, avg_transactions_per_customer):
        """Create transaction history for customers"""
        transaction_types = [
            'qr_payment', 'eft_topup', 'wallet_transfer', 
            'merchant_payment', 'deposit', 'withdrawal'
        ]
        
        total_transactions = 0
        
        for customer in customers:
            if customer.status != 'active':
                continue  # Skip inactive customers
            
            num_transactions = random.randint(
                max(1, avg_transactions_per_customer - 5),
                avg_transactions_per_customer + 5
            )
            
            for i in range(num_transactions):
                transaction_type = random.choice(transaction_types)
                
                # Generate realistic amounts based on transaction type
                if transaction_type in ['qr_payment', 'merchant_payment']:
                    amount = Decimal(str(random.uniform(10, 500))).quantize(Decimal('0.01'))
                elif transaction_type in ['eft_topup', 'deposit']:
                    amount = Decimal(str(random.uniform(100, 5000))).quantize(Decimal('0.01'))
                else:
                    amount = Decimal(str(random.uniform(50, 1000))).quantize(Decimal('0.01'))
                
                # Calculate fee
                fee = Decimal('2.00') if transaction_type == 'eft_topup' else Decimal('0.50')
                
                # Determine status (most should be completed)
                status = random.choice([
                    'completed', 'completed', 'completed', 'completed',
                    'pending', 'failed', 'cancelled'
                ])
                
                status_obj = next((s for s in transaction_statuses if s.code == status), transaction_statuses[0])
                payment_method = random.choice(payment_methods)
                
                # Create transaction date in the past
                created_at = timezone.now() - timedelta(
                    days=random.randint(1, 180),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                transaction = Transaction.objects.create(
                    transaction_type=transaction_type,
                    amount=amount,
                    fee=fee,
                    currency='BWP',
                    customer=customer,
                    merchant=customer.merchant,
                    wallet=customer.wallet if hasattr(customer, 'wallet') else None,
                    status=status_obj,
                    payment_method=payment_method,
                    description=f'{transaction_type.replace("_", " ").title()} transaction',
                    external_reference=f'EXT-{random.randint(100000, 999999)}',
                    is_reconciled=status == 'completed',
                    created_at=created_at,
                    completed_at=created_at + timedelta(minutes=random.randint(1, 30)) if status == 'completed' else None,
                    failure_reason='Insufficient funds' if status == 'failed' else '',
                    metadata={
                        'channel': random.choice(['mobile_app', 'web', 'api']),
                        'device_id': f'device_{random.randint(1000, 9999)}'
                    }
                )
                
                total_transactions += 1
        
        self.stdout.write(f'   Created {total_transactions} transactions')
    
    def create_qr_codes(self, merchants):
        """Create QR codes for merchants"""
        total_qr_codes = 0
        
        for merchant in merchants:
            if not merchant.is_active:
                continue
            
            num_qr_codes = random.randint(3, 10)
            
            for i in range(num_qr_codes):
                amount = Decimal(str(random.uniform(10, 1000))).quantize(Decimal('0.01'))
                
                status = random.choice(['active', 'active', 'used', 'expired', 'cancelled'])
                
                # Create QR code date
                created_at = timezone.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23)
                )
                
                expires_at = created_at + timedelta(minutes=random.randint(15, 1440))  # 15 min to 24 hours
                
                QRCode.objects.create(
                    merchant=merchant,
                    amount=amount,
                    reference=f'QR-REF-{random.randint(1000, 9999)}',
                    description=f'Payment for {merchant.business_name}',
                    qr_data=f'{{"merchant_id": "{merchant.merchant_id}", "amount": "{amount}"}}',
                    status=status,
                    expires_at=expires_at,
                    created_at=created_at
                )
                
                total_qr_codes += 1
        
        self.stdout.write(f'   Created {total_qr_codes} QR codes')
    
    def create_eft_payments(self, customers):
        """Create EFT payment records"""
        bank_codes = ['fnb', 'standard', 'barclays', 'nedbank', 'choppies']
        total_eft_payments = 0
        
        for customer in customers:
            if customer.status != 'active' or random.random() > 0.4:  # 40% of customers have EFT payments
                continue
            
            num_payments = random.randint(1, 5)
            
            for i in range(num_payments):
                amount = Decimal(str(random.uniform(100, 5000))).quantize(Decimal('0.01'))
                bank_code = random.choice(bank_codes)
                
                status = random.choice([
                    'completed', 'completed', 'completed',
                    'pending', 'processing', 'failed'
                ])
                
                created_at = timezone.now() - timedelta(
                    days=random.randint(1, 90),
                    hours=random.randint(0, 23)
                )
                
                eft_payment = EFTPayment.objects.create(
                    customer=customer,
                    wallet=customer.wallet if hasattr(customer, 'wallet') else None,
                    amount=amount,
                    bank_code=bank_code,
                    account_number=f'{bank_code.upper()}{random.randint(1000000, 9999999)}',
                    reference=f'EFT-{random.randint(100000, 999999)}',
                    status=status,
                    external_reference=f'BNK-{random.randint(100000, 999999)}' if status == 'completed' else None,
                    created_at=created_at,
                    processed_at=created_at + timedelta(minutes=random.randint(1, 15)) if status in ['completed', 'failed'] else None,
                    completed_at=created_at + timedelta(minutes=random.randint(15, 60)) if status == 'completed' else None,
                    response_data={
                        'bank_response': 'SUCCESS' if status == 'completed' else 'PENDING',
                        'transaction_id': f'bank_txn_{random.randint(100000, 999999)}'
                    }
                )
                
                total_eft_payments += 1
        
        self.stdout.write(f'   Created {total_eft_payments} EFT payments')
    
    def generate_api_key(self):
        """Generate a random API key"""
        return 'pk_dev_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def generate_secret_hash(self):
        """Generate a random secret hash"""
        return 'sk_dev_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(48))

