"""
Tests for Wallet Creation API
"""
import uuid
from decimal import Decimal
import django
import os
import sys
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from phantom_apps.merchants.models import Merchant
from phantom_apps.customers.models import Customer
from phantom_apps.wallets.models import Wallet

class WalletCreationAPITest(TestCase):
    """Test wallet creation API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and merchant
        self.user = User.objects.create_user(
            username='testmerchant',
            email='test@merchant.com',
            password='testpass123'
        )
        
        self.merchant = Merchant.objects.create(
            user=self.user,
            business_name='Test Business',
            fnb_account_number='1234567890',
            contact_email='test@merchant.com',
            phone_number='+26771234567',
            business_registration='TEST123',
            api_key='merchant1_test_api_key',
            api_secret_hash='merchant1_test_api_secret_hash'
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            merchant=self.merchant,
            first_name='John',
            last_name='Doe',
            phone_number='+26771234568',
            email='john@example.com',
            identity_number='123456789'
        )
        
        # Create another merchant's customer
        self.other_user = User.objects.create_user(
            username='othermerchant',
            email='other@merchant.com',
            password='testpass123'
        )
        
        self.other_merchant = Merchant.objects.create(
            user=self.other_user,
            business_name='Other Business',
            fnb_account_number='1234567891',
            contact_email='other@merchant.com',
            phone_number='+26771234569',
            business_registration='OTHER123',
            api_key='merchant2_test_api_key',
            api_secret_hash='merchant2_test_api_secret_hash'
        )
        
        self.other_customer = Customer.objects.create(
            merchant=self.other_merchant,
            first_name='Jane',
            last_name='Smith',
            phone_number='+26771234570',
            email='jane@example.com'
        )
        
        # Set up API client
        self.client = APIClient()
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
    def test_create_wallet_success(self):
        """Test successful wallet creation"""
        url = f'/api/v1/merchants/me/customers/{self.customer.customer_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['created'])
        self.assertEqual(response.data['message'], 'Wallet created successfully')
        
        # Check wallet data
        wallet_data = response.data['wallet']
        self.assertEqual(wallet_data['balance'], '0.00')
        self.assertEqual(wallet_data['currency'], 'BWP')
        self.assertEqual(wallet_data['status'], 'active')
        self.assertFalse(wallet_data['is_frozen'])
        
        # Check customer info included
        self.assertIn('customer', wallet_data)
        self.assertEqual(wallet_data['customer']['first_name'], 'John')
        
    def test_return_existing_wallet(self):
        """Test returning existing wallet"""
        # Create wallet first
        wallet = Wallet.objects.create(
            customer=self.customer,
            merchant=self.merchant,
            balance=Decimal('100.00'),
            currency='BWP'
        )
        
        url = f'/api/v1/merchants/me/customers/{self.customer.customer_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['created'])
        self.assertEqual(response.data['message'], 'Wallet already exists')
        
        # Should return existing wallet
        self.assertEqual(response.data['wallet']['wallet_id'], str(wallet.wallet_id))
        
    def test_customer_not_found(self):
        """Test error when customer doesn't exist"""
        non_existent_id = uuid.uuid4()
        url = f'/api/v1/merchants/me/customers/{non_existent_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data['error'])
        self.assertEqual(response.data['error_code'], 'CUSTOMER_NOT_FOUND')
        
    def test_customer_not_owned_by_merchant(self):
        """Test error when customer belongs to different merchant"""
        url = f'/api/v1/merchants/me/customers/{self.other_customer.customer_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(response.data['error'])
        self.assertEqual(response.data['error_code'], 'CUSTOMER_NOT_OWNED_BY_MERCHANT')
        
    def test_unauthenticated_request(self):
        """Test error when not authenticated"""
        url = f'/api/v1/merchants/me/customers/{self.customer.customer_id}/wallet/'
        
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_user_without_merchant(self):
        """Test error when user has no merchant"""
        user_no_merchant = User.objects.create_user(
            username='nomerchant',
            email='no@merchant.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(user_no_merchant)
        token = str(refresh.access_token)
        
        url = f'/api/v1/merchants/me/customers/{self.customer.customer_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error_code'], 'MERCHANT_NOT_FOUND')