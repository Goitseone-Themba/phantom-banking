from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from decimal import Decimal
from .models import Wallet, WalletCreationRequest, WalletAuditLog

User = get_user_model()

class WalletModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.merchant = User.objects.create_user(
            username='testmerchant',
            email='merchant@test.com',
            password='testpass123'
        )
        
        # Create test wallet
        self.wallet = Wallet.objects.create(
            wallet_id='TEST123',
            user=self.user,
            merchant=self.merchant,
            balance=Decimal('1000.00'),
            status='active',
            wallet_type='basic'
        )

    def test_wallet_creation(self):
        """Test wallet creation with default values"""
        self.assertEqual(self.wallet.wallet_id, 'TEST123')
        self.assertEqual(self.wallet.balance, Decimal('1000.00'))
        self.assertEqual(self.wallet.status, 'active')
        self.assertEqual(self.wallet.wallet_type, 'basic')
        self.assertEqual(self.wallet.daily_transaction_count, 0)
        self.assertEqual(self.wallet.monthly_transaction_count, 0)

    def test_transaction_allowed_checks(self):
        """Test transaction validation logic"""
        # Test with valid amount
        allowed, message = self.wallet.is_transaction_allowed(Decimal('500.00'))
        self.assertTrue(allowed)
        self.assertEqual(message, 'Transaction allowed')

        # Test with insufficient funds
        allowed, message = self.wallet.is_transaction_allowed(Decimal('2000.00'))
        self.assertFalse(allowed)
        self.assertEqual(message, 'Insufficient funds')

        # Test with blocked wallet
        self.wallet.status = 'blocked'
        self.wallet.save()
        allowed, message = self.wallet.is_transaction_allowed(Decimal('100.00'))
        self.assertFalse(allowed)
        self.assertEqual(message, 'Wallet is not active')

        # Test daily limit
        self.wallet.status = 'active'
        self.wallet.daily_transaction_amount = Decimal('900.00')
        self.wallet.save()
        allowed, message = self.wallet.is_transaction_allowed(Decimal('200.00'))
        self.assertFalse(allowed)
        self.assertEqual(message, 'Daily transaction limit exceeded')

class WalletCreationRequestTests(TestCase):
    def setUp(self):
        from django.utils import timezone
        from datetime import date
        
        # Create test merchant
        self.merchant = User.objects.create_user(
            username='testmerchant',
            email='merchant@test.com',
            password='testpass123'
        )
        
        # Create test wallet request
        self.request = WalletCreationRequest.objects.create(
            merchant=self.merchant,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='1234567890',
            national_id='ID123456',
            date_of_birth=date(1990, 1, 1)
        )

    def test_notification_email(self):
        """Test that notification email includes active status"""
        self.request.send_notification_email()
        
        # Test that one message has been sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Verify the subject indicates active status
        self.assertEqual(mail.outbox[0].subject, 'Your Active Wallet Has Been Created')
        
        # Verify the email was sent to the correct recipient
        self.assertEqual(mail.outbox[0].to[0], 'john@example.com')

class WalletAuditLogTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.merchant = User.objects.create_user(
            username='testmerchant',
            email='merchant@test.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        
        # Create test wallet
        self.wallet = Wallet.objects.create(
            wallet_id='TEST123',
            user=self.user,
            merchant=self.merchant,
            balance=Decimal('1000.00')
        )

    def test_audit_log_creation(self):
        """Test creating audit log entries"""
        log = WalletAuditLog.objects.create(
            wallet=self.wallet,
            action='create',
            actor=self.admin,
            details={'initial_balance': '1000.00'},
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(log.wallet, self.wallet)
        self.assertEqual(log.action, 'create')
        self.assertEqual(log.actor, self.admin)
        self.assertEqual(log.details['initial_balance'], '1000.00')
        self.assertEqual(log.ip_address, '127.0.0.1')