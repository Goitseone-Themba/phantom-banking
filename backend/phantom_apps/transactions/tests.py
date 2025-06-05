import json
import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from .models import QRCode, EFTPayment, Transaction
from .services import QRCodeService, EFTPaymentService
from ..customers.models import Customer
from ..merchants.models import Merchant
from ..wallets.models import Wallet


class QRCodeServiceTest(TestCase):
    """Test QR Code service functionality"""
    
    def setUp(self):
        self.merchant = Merchant.objects.create(
            business_name="Test Merchant",
            contact_email="test@merchant.com"
        )
        self.customer = Customer.objects.create(
            phone_number="71234567",
            full_name="Test Customer"
        )
        self.wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('1000.00')
        )
    
    def test_create_qr_code(self):
        """Test QR code creation"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.id),
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
            merchant_id=str(self.merchant.id),
            amount=Decimal('50.00')
        )
        
        transaction_obj = QRCodeService.process_qr_payment(
            qr_code=qr_code,
            customer_phone=self.customer.phone_number,
            wallet_id=str(self.wallet.id)
        )
        
        self.assertEqual(transaction_obj.status, 'completed')
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
            merchant_id=str(self.merchant.id),
            amount=Decimal('50.00')
        )
        
        with self.assertRaises(ValueError) as context:
            QRCodeService.process_qr_payment(
                qr_code=qr_code,
                customer_phone=self.customer.phone_number,
                wallet_id=str(self.wallet.id)
            )
        
        self.assertIn("Insufficient wallet balance", str(context.exception))


class EFTPaymentServiceTest(TestCase):
    """Test EFT Payment service functionality"""
    
    def setUp(self):
        self.merchant = Merchant.objects.create(
            business_name="Test Merchant",
            contact_email="test@merchant.com"
        )
        self.customer = Customer.objects.create(
            phone_number="71234567",
            full_name="Test Customer"
        )
        self.wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('100.00')
        )
    
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
            wallet_id=str(self.wallet.id),
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


class QRCodeAPITest(APITestCase):
    """Test QR Code API endpoints"""
    
    def setUp(self):
        self.merchant = Merchant.objects.create(
            business_name="Test Merchant",
            contact_email="test@merchant.com"
        )
        self.customer = Customer.objects.create(
            phone_number="71234567",
            full_name="Test Customer"
        )
        self.wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('1000.00')
        )
    
    def test_create_qr_code_api(self):
        """Test QR code creation via API"""
        url = reverse('transactions:qr-create')
        data = {
            'merchant_id': str(self.merchant.id),
            'amount': '50.00',
            'description': 'Test payment',
            'expires_in_minutes': 30
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('qr_token', response.data)
        self.assertEqual(response.data['amount'], '50.00')
        self.assertEqual(response.data['merchant_name'], 'Test Merchant')
    
    def test_get_qr_code_details(self):
        """Test retrieving QR code details"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.id),
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
            merchant_id=str(self.merchant.id),
            amount=Decimal('50.00')
        )
        
        url = reverse('transactions:qr-payment', kwargs={'qr_token': qr_code.qr_token})
        data = {
            'customer_phone': self.customer.phone_number,
            'wallet_id': str(self.wallet.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['amount'], '50.00')
    
    def test_get_qr_image(self):
        """Test QR code image generation"""
        qr_code = QRCodeService.create_qr_code(
            merchant_id=str(self.merchant.id),
            amount=Decimal('50.00')
        )
        
        url = reverse('transactions:qr-image', kwargs={'qr_token': qr_code.qr_token})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertIn('data:image/png;base64,', response.data['image'])


class EFTPaymentAPITest(APITestCase):
    """Test EFT Payment API endpoints"""
    
    def setUp(self):
        self.merchant = Merchant.objects.create(
            business_name="Test Merchant",
            contact_email="test@merchant.com"
        )
        self.customer = Customer.objects.create(
            phone_number="71234567",
            full_name="Test Customer"
        )
        self.wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('100.00')
        )
    
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
            'wallet_id': str(self.wallet.id),
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


class TransactionAPITest(APITestCase):
    """Test Transaction API endpoints"""
    
    def setUp(self):
        self.merchant = Merchant.objects.create(
            business_name="Test Merchant",
            contact_email="test@merchant.com"
        )
        self.customer = Customer.objects.create(
            phone_number="71234567",
            full_name="Test Customer"
        )
        self.wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('1000.00')
        )
        
        # Create sample transactions
        self.transaction1 = Transaction.objects.create(
            transaction_type='qr_payment',
            amount=Decimal('50.00'),
            fee=Decimal('2.00'),
            net_amount=Decimal('50.00'),
            from_wallet=self.wallet,
            customer=self.customer,
            merchant=self.merchant,
            status='completed',
            description='Test QR Payment'
        )
        
        self.transaction2 = Transaction.objects.create(
            transaction_type='eft_topup',
            amount=Decimal('100.00'),
            fee=Decimal('5.00'),
            net_amount=Decimal('95.00'),
            to_wallet=self.wallet,
            customer=self.customer,
            status='completed',
            description='Test EFT Top-up'
        )
    
    def test_list_transactions(self):
        """Test transaction listing API"""
        url = reverse('transactions:transaction-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_transactions_by_customer(self):
        """Test filtering transactions by customer"""
        url = reverse('transactions:transaction-list')
        response = self.client.get(url, {'customer_phone': self.customer.phone_number})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        for transaction in response.data:
            self.assertEqual(transaction['customer_phone'], self.customer.phone_number)
    
    def test_filter_transactions_by_type(self):
        """Test filtering transactions by type"""
        url = reverse('transactions:transaction-list')
        response = self.client.get(url, {'type': 'qr_payment'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['transaction_type'], 'qr_payment')
    
    def test_filter_transactions_by_merchant(self):
        """Test filtering transactions by merchant"""
        url = reverse('transactions:transaction-list')
        response = self.client.get(url, {'merchant_id': str(self.merchant.id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only QR payment has merchant
        self.assertEqual(response.data[0]['merchant_name'], self.merchant.business_name)


class IntegrationTest(APITestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        self.merchant = Merchant.objects.create(
            business_name="Integration Test Merchant",
            contact_email="integration@test.com"
        )
        self.customer = Customer.objects.create(
            phone_number="72345678",
            full_name="Integration Test Customer"
        )
        self.wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('2000.00')
        )
    
    def test_complete_qr_payment_flow(self):
        """Test complete QR payment flow from creation to completion"""
        # Step 1: Create QR code
        create_url = reverse('transactions:qr-create')
        create_data = {
            'merchant_id': str(self.merchant.id),
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
            'wallet_id': str(self.wallet.id)
        }
        
        initial_balance = self.wallet.balance
        payment_response = self.client.post(payment_url, payment_data, format='json')
        self.assertEqual(payment_response.status_code, status.HTTP_200_OK)
        self.assertEqual(payment_response.data['status'], 'completed')
        
        # Step 5: Verify wallet balance updated
        self.wallet.refresh_from_db()
        expected_balance = initial_balance - Decimal('75.50') - Decimal('2.00')  # amount + fee
        self.assertEqual(self.wallet.balance, expected_balance)
        
        # Step 6: Verify QR code is now used
        detail_response2 = self.client.get(detail_url)
        self.assertEqual(detail_response2.data['status'], 'used')
        
        # Step 7: Verify transaction appears in list
        transactions_url = reverse('transactions:transaction-list')
        transactions_response = self.client.get(
            transactions_url, 
            {'customer_phone': self.customer.phone_number}
        )
        self.assertEqual(transactions_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(transactions_response.data), 1)
    
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
            'wallet_id': str(self.wallet.id),
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
        
        # Step 6: Verify transaction created
        transactions_url = reverse('transactions:transaction-list')
        transactions_response = self.client.get(
            transactions_url,
            {'customer_phone': self.customer.phone_number, 'type': 'eft_topup'}
        )
        self.assertEqual(transactions_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(transactions_response.data), 1)


class ErrorHandlingTest(APITestCase):
    """Test error handling scenarios"""
    
    def setUp(self):
        self.merchant = Merchant.objects.create(
            business_name="Error Test Merchant",
            contact_email="error@test.com"
        )
    
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
        customer = Customer.objects.create(phone_number="71111111", full_name="Test")
        wallet = Wallet.objects.create(customer=customer, merchant=self.merchant)
        
        for i in range(150):
            Transaction.objects.create(
                transaction_type='qr_payment',
                amount=Decimal('10.00'),
                customer=customer,
                status='completed',
                description=f'Test transaction {i}'
            )
        
        url = reverse('transactions:transaction-list')
        response = self.client.get(url, {'customer_phone': customer.phone_number})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 100)  # Should be limited to 100