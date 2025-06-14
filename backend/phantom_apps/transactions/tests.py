import json
import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from .models import Transaction, PaymentMethod, TransactionStatus, QRCode, EFTPayment
from .services import TransactionService, QRCodeService, EFTPaymentService
from ..wallets.models import Wallet
from ..merchants.models import Merchant
from ..customers.models import Customer


class TestDataMixin:
    """Mixin for common test data setup"""
    
    def setUp(self):
        # Create payment methods and statuses
        self.qr_method = PaymentMethod.objects.create(code='qr_code', name='QR Code Payment')
        self.eft_method = PaymentMethod.objects.create(code='eft', name='Electronic Fund Transfer')
        
        self.pending_status = TransactionStatus.objects.create(
            code='pending', name='Pending', description='Transaction is pending'
        )
        self.completed_status = TransactionStatus.objects.create(
            code='completed', name='Completed', description='Transaction is completed'
        )
        self.failed_status = TransactionStatus.objects.create(
            code='failed', name='Failed', description='Transaction failed'
        )
        
        # Create user, merchant, customer, and wallet
        self.user = User.objects.create_user(username='testmerchant', password='password')
        self.merchant = Merchant.objects.create(
            user=self.user,
            business_name='Test Business',
            contact_email='test@business.com',
            phone_number='+26771234567'
        )
        self.customer = Customer.objects.create(
            merchant=self.merchant,
            first_name='John',
            last_name='Doe',
            phone_number='71234567',
            email='john@example.com'
        )
        self.wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('1000.00'),
            currency='BWP',
            status='active'
        )


class TransactionModelsTestCase(TestCase, TestDataMixin):
    """Test case for transaction models"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        TestCase.setUp(self)
    
    def test_transaction_creation(self):
        """Test transaction model creation"""
        transaction = Transaction.objects.create(
            wallet=self.wallet,
            merchant=self.merchant,
            customer=self.customer,
            amount=Decimal('100.00'),
            transaction_type='payment',
            status=self.completed_status,
            payment_method=self.qr_method,
            reference='TEST_REF_001',
            description='Test payment'
        )
        
        self.assertIsNotNone(transaction.transaction_id)
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.transaction_type, 'payment')
        self.assertEqual(transaction.status, self.completed_status)
        self.assertEqual(transaction.payment_method, self.qr_method)
        self.assertEqual(transaction.reference, 'TEST_REF_001')
        self.assertEqual(transaction.description, 'Test payment')
        self.assertEqual(transaction.merchant, self.merchant)
        self.assertEqual(transaction.wallet, self.wallet)
        self.assertIsNotNone(transaction.reference_number)
    
    def test_qr_code_creation(self):
        """Test QR code model creation"""
        qr_code = QRCode.objects.create(
            merchant=self.merchant,
            amount=Decimal('50.00'),
            description='Test QR payment'
        )
        
        self.assertIsNotNone(qr_code.qr_token)
        self.assertEqual(qr_code.amount, Decimal('50.00'))
        self.assertEqual(qr_code.status, 'active')
        self.assertTrue(qr_code.is_valid)
        self.assertFalse(qr_code.is_expired)
    
    def test_eft_payment_creation(self):
        """Test EFT payment model creation"""
        eft_payment = EFTPayment.objects.create(
            customer=self.customer,
            wallet=self.wallet,
            amount=Decimal('100.00'),
            bank_code='fnb',
            account_number='1234567890',
            reference='TEST-EFT-001'
        )
        
        self.assertEqual(eft_payment.amount, Decimal('100.00'))
        self.assertEqual(eft_payment.bank_code, 'fnb')
        self.assertEqual(eft_payment.status, 'pending')


class TransactionServiceTestCase(TestCase, TestDataMixin):
    """Test case for transaction service"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        TestCase.setUp(self)
    
    def test_process_qr_payment(self):
        """Test QR payment processing"""
        transaction_obj = TransactionService.process_qr_payment(
            merchant=self.merchant,
            wallet_id=self.wallet.wallet_id,
            amount=Decimal('100.00'),
            qr_code='QR_CODE_TEST_12345',
            reference='TEST_QR_REF_001',
            description='Test QR payment'
        )
        
        # Check transaction was created
        self.assertIsNotNone(transaction_obj)
        self.assertEqual(transaction_obj.amount, Decimal('100.00'))
        self.assertEqual(transaction_obj.transaction_type, 'payment')
        self.assertEqual(transaction_obj.reference, 'TEST_QR_REF_001')
        self.assertEqual(transaction_obj.description, 'Test QR payment')
        
        # Check wallet balance was updated
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('900.00'))
    
    def test_process_eft_payment(self):
        """Test EFT payment processing"""
        transaction_obj = TransactionService.process_eft_payment(
            merchant=self.merchant,
            wallet_id=self.wallet.wallet_id,
            amount=Decimal('200.00'),
            bank_name='Test Bank',
            account_number='12345678901234',
            reference='TEST_EFT_REF_001',
            description='Test EFT payment'
        )
        
        # Check transaction was created
        self.assertIsNotNone(transaction_obj)
        self.assertEqual(transaction_obj.amount, Decimal('200.00'))
        self.assertEqual(transaction_obj.transaction_type, 'payment')
        self.assertEqual(transaction_obj.reference, 'TEST_EFT_REF_001')
        self.assertEqual(transaction_obj.description, 'Test EFT payment')
        
        # Check wallet balance was updated
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('800.00'))


class QRCodeServiceTestCase(TestCase, TestDataMixin):
    """Test QR Code service functionality"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        TestCase.setUp(self)
    
    def test_create_qr_code(self):
        """Test QR code creation"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.merchant_id),
            amount=Decimal('50.00'),
            description="Test payment"
        )
        
        self.assertIsNotNone(qr_code.qr_token)
        self.assertEqual(qr_code.amount, Decimal('50.00'))
        self.assertEqual(qr_code.merchant, self.merchant)
        self.assertEqual(qr_code.status, 'active')
        self.assertTrue(qr_code.is_valid)
    
    def test_process_qr_payment_success(self):
        """Test successful QR payment processing"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.merchant_id),
            amount=Decimal('50.00')
        )
        
        transaction_obj = QRCodeService.process_qr_payment(
            qr_code=qr_code,
            customer_phone=self.customer.phone_number,
            wallet_id=str(self.wallet.wallet_id)
        )
        
        self.assertEqual(transaction_obj.status.code, 'completed')
        self.assertEqual(transaction_obj.amount, Decimal('50.00'))
        self.assertEqual(transaction_obj.transaction_type, 'qr_payment')
        
        # Check wallet balance updated
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('948.00'))  # 1000 - 50 - 2 fee
        
        # Check QR code marked as used
        qr_code.refresh_from_db()
        self.assertEqual(qr_code.status, 'used')
    
    def test_process_qr_payment_insufficient_balance(self):
        """Test QR payment with insufficient balance"""
        self.wallet.balance = Decimal('10.00')
        self.wallet.save()
        
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.merchant_id),
            amount=Decimal('50.00')
        )
        
        with self.assertRaises(ValueError) as context:
            QRCodeService.process_qr_payment(
                qr_code=qr_code,
                customer_phone=self.customer.phone_number,
                wallet_id=str(self.wallet.wallet_id)
            )
        
        self.assertIn("Insufficient wallet balance", str(context.exception))


class EFTPaymentServiceTestCase(TestCase, TestDataMixin):
    """Test EFT Payment service functionality"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        TestCase.setUp(self)
    
    @patch('phantom_apps.transactions.services.EFTPaymentService._process_with_bank')
    def test_initiate_eft_payment_success(self, mock_bank_process):
        """Test successful EFT payment initiation"""
        mock_bank_process.return_value = {
            'status': 'completed',
            'reference': 'BNK-123456',
            'transaction_id': 'TXN-7890123'
        }
        
        eft_payment = EFTPaymentService.initiate_eft_payment(
            customer_phone=self.customer.phone_number,
            wallet_id=str(self.wallet.wallet_id),
            amount=Decimal('100.00'),
            bank_code='fnb',
            account_number='1234567890'
        )
        
        self.assertEqual(eft_payment.status, 'processing')
        self.assertEqual(eft_payment.amount, Decimal('100.00'))
        self.assertEqual(eft_payment.bank_code, 'fnb')
        self.assertEqual(eft_payment.external_reference, 'BNK-123456')
    
    def test_process_webhook_completed(self):
        """Test webhook processing for completed payment"""
        eft_payment = EFTPayment.objects.create(
            customer=self.customer,
            wallet=self.wallet,
            amount=Decimal('100.00'),
            bank_code='fnb',
            account_number='1234567890',
            external_reference='BNK-123456',
            status='processing'
        )
        
        initial_balance = self.wallet.balance
        
        webhook_data = {
            'status': 'completed',
            'fee': '5.00',
            'timestamp': timezone.now().isoformat()
        }
        
        result = EFTPaymentService.process_webhook('BNK-123456', webhook_data)
        
        self.assertTrue(result)
        
        eft_payment.refresh_from_db()
        self.assertEqual(eft_payment.status, 'completed')
        self.assertIsNotNone(eft_payment.completed_at)
        self.assertIsNotNone(eft_payment.transaction)
        
        # Check wallet balance updated (amount - fee)
        self.wallet.refresh_from_db()
        expected_balance = initial_balance + Decimal('95.00')  # 100 - 5 fee
        self.assertEqual(self.wallet.balance, expected_balance)


class MerchantAPITestCase(APITestCase, TestDataMixin):
    """Test case for merchant-authenticated API endpoints"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        APITestCase.setUp(self)
        # Create client and authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_process_qr_payment_api(self):
        """Test QR payment API endpoint"""
        url = reverse('transactions:merchant-qr-payment')
        data = {
            'wallet_id': str(self.wallet.wallet_id),
            'amount': '100.00',
            'qr_code': 'QR_CODE_TEST_12345',
            'reference': 'TEST_QR_API_001',
            'description': 'Test QR payment via API'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'QR Payment processed successfully')
        
        # Check wallet balance was updated
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('900.00'))
    
    def test_process_eft_payment_api(self):
        """Test EFT payment API endpoint"""
        url = reverse('transactions:merchant-eft-payment')
        data = {
            'wallet_id': str(self.wallet.wallet_id),
            'amount': '200.00',
            'bank_name': 'Test Bank',
            'account_number': '12345678901234',
            'reference': 'TEST_EFT_API_001',
            'description': 'Test EFT payment via API'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'EFT Payment processed successfully')
        
        # Check wallet balance was updated
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('800.00'))
    
    def test_transaction_summary_api(self):
        """Test transaction summary API"""
        # Create some test transactions first
        TransactionService.process_qr_payment(
            merchant=self.merchant,
            wallet_id=self.wallet.wallet_id,
            amount=Decimal('50.00'),
            qr_code='QR_TEST_1'
        )
        
        url = reverse('transactions:merchant-transactions-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_transactions', response.data)
        self.assertIn('transaction_volumes', response.data)


class PublicAPITestCase(APITestCase, TestDataMixin):
    """Test case for public API endpoints"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        APITestCase.setUp(self)
        self.client = APIClient()
    
    def test_create_qr_code_api(self):
        """Test QR code creation via API"""
        url = reverse('transactions:qr-create')
        data = {
            'merchant_id': str(self.merchant.merchant_id),
            'amount': '50.00',
            'description': 'Test payment',
            'expires_in_minutes': 30
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('qr_token', response.data)
        self.assertEqual(response.data['amount'], '50.00')
        self.assertEqual(response.data['merchant_name'], 'Test Business')
    
    def test_get_qr_code_details(self):
        """Test retrieving QR code details"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.merchant_id),
            amount=Decimal('50.00')
        )
        
        url = reverse('transactions:qr-detail', kwargs={'qr_token': qr_code.qr_token})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['qr_token'], qr_code.qr_token)
        self.assertEqual(response.data['amount'], '50.00')
    
    def test_process_qr_payment_api(self):
        """Test QR payment processing via API"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.merchant_id),
            amount=Decimal('50.00')
        )
        
        url = reverse('transactions:qr-payment', kwargs={'qr_token': qr_code.qr_token})
        data = {
            'customer_phone': self.customer.phone_number,
            'wallet_id': str(self.wallet.wallet_id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status']['code'], 'completed')
        self.assertEqual(response.data['amount'], '50.00')
    
    def test_get_qr_image(self):
        """Test QR code image generation"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.merchant_id),
            amount=Decimal('50.00')
        )
        
        url = reverse('transactions:qr-image', kwargs={'qr_token': qr_code.qr_token})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertIn('data:image/png;base64,', response.data['image'])
    
    @patch('phantom_apps.transactions.services.EFTPaymentService._process_with_bank')
    def test_initiate_eft_payment_api(self, mock_bank_process):
        """Test EFT payment initiation via API"""
        mock_bank_process.return_value = {
            'status': 'completed',
            'reference': 'BNK-123456'
        }
        
        url = reverse('transactions:eft-initiate')
        data = {
            'customer_phone': self.customer.phone_number,
            'wallet_id': str(self.wallet.wallet_id),
            'amount': '100.00',
            'bank_code': 'fnb',
            'account_number': '1234567890',
            'reference': 'TEST-TOPUP'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'processing')
        self.assertEqual(response.data['amount'], '100.00')
        self.assertEqual(response.data['bank_code'], 'fnb')
    
    def test_eft_payment_status_api(self):
        """Test EFT payment status check via API"""
        eft_payment = EFTPayment.objects.create(
            customer=self.customer,
            wallet=self.wallet,
            amount=Decimal('100.00'),
            bank_code='fnb',
            account_number='1234567890',
            status='processing'
        )
        
        url = reverse('transactions:eft-status', kwargs={'id': eft_payment.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'processing')
        self.assertEqual(response.data['amount'], '100.00')
    
    def test_eft_webhook_api(self):
        """Test EFT webhook processing via API"""
        eft_payment = EFTPayment.objects.create(
            customer=self.customer,
            wallet=self.wallet,
            amount=Decimal('100.00'),
            bank_code='fnb',
            account_number='1234567890',
            external_reference='BNK-123456',
            status='processing'
        )
        
        url = reverse('transactions:eft-webhook')
        data = {
            'reference': 'BNK-123456',
            'status': 'completed',
            'fee': '5.00'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['processed'])
        
        eft_payment.refresh_from_db()
        self.assertEqual(eft_payment.status, 'completed')
    
    def test_transaction_list_api(self):
        """Test transaction list API"""
        # Create sample transactions
        QRCodeService.process_qr_payment(
            qr_code=QRCodeService.create_qr_code(
                merchant_id=str(self.merchant.merchant_id),
                amount=Decimal('50.00')
            ),
            customer_phone=self.customer.phone_number,
            wallet_id=str(self.wallet.wallet_id)
        )
        
        url = reverse('transactions:transaction-list')
        response = self.client.get(url, {'customer_phone': self.customer.phone_number})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class IntegrationTestCase(APITestCase, TestDataMixin):
    """End-to-end integration tests"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        APITestCase.setUp(self)
        self.client = APIClient()
    
    def test_complete_qr_payment_flow(self):
        """Test complete QR payment flow from creation to completion"""
        # Step 1: Create QR code
        create_url = reverse('transactions:qr-create')
        create_data = {
            'merchant_id': str(self.merchant.merchant_id),
            'amount': '75.50',
            'description': 'Integration test payment',
            'expires_in_minutes': 30
        }
        
        create_response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        qr_token = create_response.data['qr_token']
        
        # Step 2: Get QR code details
        detail_url = reverse('transactions:qr-detail', kwargs={'qr_token': qr_token})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertTrue(detail_response.data['is_valid'])
        
        # Step 3: Get QR code image
        image_url = reverse('transactions:qr-image', kwargs={'qr_token': qr_token})
        image_response = self.client.get(image_url)
        self.assertEqual(image_response.status_code, status.HTTP_200_OK)
        self.assertIn('image', image_response.data)
        
        # Step 4: Process payment
        payment_url = reverse('transactions:qr-payment', kwargs={'qr_token': qr_token})
        payment_data = {
            'customer_phone': self.customer.phone_number,
            'wallet_id': str(self.wallet.wallet_id)
        }
        
        initial_balance = self.wallet.balance
        payment_response = self.client.post(payment_url, payment_data, format='json')
        self.assertEqual(payment_response.status_code, status.HTTP_200_OK)
        self.assertEqual(payment_response.data['status']['code'], 'completed')
        
        # Step 5: Verify wallet balance updated
        self.wallet.refresh_from_db()
        expected_balance = initial_balance - Decimal('75.50') - Decimal('2.00')  # amount + fee
        self.assertEqual(self.wallet.balance, expected_balance)
        
        # Step 6: Verify QR code is now used
        detail_response2 = self.client.get(detail_url)
        self.assertEqual(detail_response2.data['status'], 'used')
    
    @patch('phantom_apps.transactions.services.EFTPaymentService._process_with_bank')
    def test_complete_eft_payment_flow(self, mock_bank_process):
        """Test complete EFT payment flow from initiation to completion"""
        mock_bank_process.return_value = {
            'status': 'completed',
            'reference': 'BNK-INTEGRATION-123',
            'transaction_id': 'TXN-INT-456'
        }
        
        # Step 1: Initiate EFT payment
        initiate_url = reverse('transactions:eft-initiate')
        initiate_data = {
            'customer_phone': self.customer.phone_number,
            'wallet_id': str(self.wallet.wallet_id),
            'amount': '200.00',
            'bank_code': 'fnb',
            'account_number': '9876543210',
            'reference': 'INTEGRATION-TOPUP'
        }
        
        initiate_response = self.client.post(initiate_url, initiate_data, format='json')
        self.assertEqual(initiate_response.status_code, status.HTTP_201_CREATED)
        
        eft_payment_id = initiate_response.data['id']
        external_reference = initiate_response.data['external_reference']
        
        # Step 2: Check status
        status_url = reverse('transactions:eft-status', kwargs={'id': eft_payment_id})
        status_response = self.client.get(status_url)
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data['status'], 'processing')
        
        # Step 3: Simulate webhook completion
        webhook_url = reverse('transactions:eft-webhook')
        webhook_data = {
            'reference': external_reference,
            'status': 'completed',
            'fee': '10.00',
            'timestamp': timezone.now().isoformat()
        }
        
        initial_balance = self.wallet.balance
        webhook_response = self.client.post(webhook_url, webhook_data, format='json')
        self.assertEqual(webhook_response.status_code, status.HTTP_200_OK)
        self.assertTrue(webhook_response.data['processed'])
        
        # Step 4: Verify final status
        status_response2 = self.client.get(status_url)
        self.assertEqual(status_response2.data['status'], 'completed')
        
        # Step 5: Verify wallet balance updated
        self.wallet.refresh_from_db()
        expected_balance = initial_balance + Decimal('190.00')  # 200 - 10 fee
        self.assertEqual(self.wallet.balance, expected_balance)


class ErrorHandlingTestCase(APITestCase, TestDataMixin):
    """Test error handling scenarios"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        APITestCase.setUp(self)
        self.client = APIClient()
    
    def test_qr_payment_with_invalid_token(self):
        """Test QR payment with invalid token"""
        url = reverse('transactions:qr-payment', kwargs={'qr_token': 'INVALID_TOKEN'})
        data = {
            'customer_phone': '71234567',
            'wallet_id': str(uuid.uuid4())
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_qr_payment_with_expired_token(self):
        """Test QR payment with expired token"""
        qr_code = QRCode.objects.create(
            merchant=self.merchant,
            amount=Decimal('50.00'),
            expires_at=timezone.now() - timezone.timedelta(hours=1),  # Expired
            status='active'
        )
        
        url = reverse('transactions:qr-payment', kwargs={'qr_token': qr_code.qr_token})
        data = {
            'customer_phone': '71234567',
            'wallet_id': str(uuid.uuid4())
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('invalid or expired', response.data['error'])
    
    def test_eft_payment_with_invalid_bank_code(self):
        """Test EFT payment with invalid bank code"""
        url = reverse('transactions:eft-initiate')
        data = {
            'customer_phone': '71234567',
            'wallet_id': str(uuid.uuid4()),
            'amount': '100.00',
            'bank_code': 'invalid_bank',
            'account_number': '1234567890'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_transaction_list_with_large_limit(self):
        """Test transaction list respects limit"""
        # Create 150 transactions (more than the 100 limit)
        for i in range(150):
            Transaction.objects.create(
                transaction_type='qr_payment',
                amount=Decimal('10.00'),
                customer=self.customer,
                status=self.completed_status,
                description=f'Test transaction {i}'
            )
        
        url = reverse('transactions:transaction-list')
        response = self.client.get(url, {'customer_phone': self.customer.phone_number})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 100)  # Should be limited to 100


class PerformanceTestCase(APITestCase, TestDataMixin):
    """Test performance and concurrency scenarios"""
    
    def setUp(self):
        TestDataMixin.setUp(self)
        APITestCase.setUp(self)
        self.client = APIClient()
    
    def test_concurrent_qr_code_creation(self):
        """Test QR code creation performance with multiple sequential requests"""
        # Since Django test database doesn't work well with threading,
        # we'll test performance with rapid sequential requests instead
        import time
        
        results = []
        errors = []
        
        start_time = time.time()
        
        # Create 10 QR codes rapidly in sequence
        for i in range(10):
            try:
                url = reverse('transactions:qr-create')
                data = {
                    'merchant_id': str(self.merchant.merchant_id),
                    'amount': '50.00',
                    'description': f'Performance test {i}'
                }
                response = self.client.post(url, data, format='json')
                results.append(response.status_code)
                if response.status_code != 201:
                    errors.append(f"Request {i}: {response.status_code} - {response.data}")
            except Exception as e:
                errors.append(f"Request {i}: Exception - {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Debug: print errors if any
        if errors:
            print(f"Errors in performance test: {errors}")
        
        # All requests should succeed
        self.assertEqual(len(results), 10)
        self.assertTrue(all(code == 201 for code in results))
        
        # Should complete reasonably quickly (within 5 seconds for 10 requests)
        self.assertLess(total_time, 5.0, f"QR code creation took too long: {total_time:.2f}s")
    
    def test_large_transaction_query(self):
        """Test querying large number of transactions"""
        # Create 1000 transactions
        transactions = []
        for i in range(1000):
            transactions.append(Transaction(
                transaction_type='qr_payment',
                amount=Decimal('10.00'),
                customer=self.customer,
                status=self.completed_status,
                description=f'Bulk test transaction {i}'
            ))
        
        Transaction.objects.bulk_create(transactions)
        
        # Query should still be fast and limited
        url = reverse('transactions:transaction-list')
        response = self.client.get(url, {'customer_phone': self.customer.phone_number})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 100)


if __name__ == '__main__':
    import unittest
    unittest.main()