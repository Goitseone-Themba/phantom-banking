"""
Tests for Customer Association API endpoints
"""
import uuid
from decimal import Decimal
import os
import sys
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from phantom_apps.merchants.models import Merchant
from phantom_apps.customers.models import Customer
from phantom_apps.wallets.models import Wallet

class CustomerAssociationAPITest(TestCase):
    """Test customer association API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users and merchants
        self.user1 = User.objects.create_user(
            username='merchant1',
            email='merchant1@test.com',
            password='testpass123'
        )
        
        self.merchant1 = Merchant.objects.create(
            user=self.user1,
            business_name='Merchant 1',
            fnb_account_number='1111111111',
            contact_email='merchant1@test.com',
            phone_number='+26771111111',
            business_registration='MERCH1',
            api_key='merchant1_api_key',
            api_secret_hash='merchant1_secret_hash'
        )
        
        self.user2 = User.objects.create_user(
            username='merchant2',
            email='merchant2@test.com',
            password='testpass123'
        )
        
        self.merchant2 = Merchant.objects.create(
            user=self.user2,
            business_name='Merchant 2',
            fnb_account_number='2222222222',
            contact_email='merchant2@test.com',
            phone_number='+26772222222',
            business_registration='MERCH2',
            api_key='merchant2_api_key',
            api_secret_hash='merchant2_secret_hash'
        )
        
        # Create customers for merchant1
        self.customer1 = Customer.objects.create(
            merchant=self.merchant1,
            first_name='John',
            last_name='Doe',
            phone_number='+26771234567',
            email='john@test.com',
            identity_number='ID001'
        )
        
        self.customer2 = Customer.objects.create(
            merchant=self.merchant1,
            first_name='Jane',
            last_name='Smith',
            phone_number='+26771234568',
            email='jane@test.com',
            identity_number='ID002'
        )
        
        # Create customer for merchant2
        self.customer3 = Customer.objects.create(
            merchant=self.merchant2,
            first_name='Bob',
            last_name='Wilson',
            phone_number='+26771234569',
            email='bob@test.com',
            identity_number='ID003'
        )
        
        # Create wallets
        self.wallet1 = Wallet.objects.create(
            customer=self.customer1,
            merchant=self.merchant1,
            balance=Decimal('100.00'),
            currency='BWP',
            status='active'
        )
        
        self.wallet2 = Wallet.objects.create(
            customer=self.customer2,
            merchant=self.merchant1,
            balance=Decimal('250.50'),
            currency='BWP',
            status='frozen'
        )
        
        self.wallet3 = Wallet.objects.create(
            customer=self.customer3,
            merchant=self.merchant2,
            balance=Decimal('75.00'),
            currency='BWP',
            status='active'
        )
        
        # Set up API client and tokens
        self.client = APIClient()
        
        refresh1 = RefreshToken.for_user(self.user1)
        self.token1 = str(refresh1.access_token)
        
        refresh2 = RefreshToken.for_user(self.user2)
        self.token2 = str(refresh2.access_token)
    
    def test_get_customer_wallet_success(self):
        """Test successful customer wallet retrieval"""
        url = f'/api/v1/customers/{self.customer1.customer_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Customer wallet retrieved successfully')
        
        # Check wallet data
        wallet_data = response.data['wallet']
        self.assertEqual(wallet_data['wallet_id'], str(self.wallet1.wallet_id))
        self.assertEqual(wallet_data['balance'], '100.00')
        self.assertEqual(wallet_data['status'], 'active')
        
        # Check customer info included
        self.assertIn('customer', wallet_data)
        self.assertEqual(wallet_data['customer']['first_name'], 'John')
    
    def test_get_customer_wallet_not_owned(self):
        """Test error when trying to access wallet of customer from different merchant"""
        url = f'/api/v1/customers/{self.customer3.customer_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(response.data['error'])
        self.assertEqual(response.data['error_code'], 'CUSTOMER_NOT_OWNED_BY_MERCHANT')
    
    def test_get_customer_wallet_not_found(self):
        """Test error when customer doesn't exist"""
        non_existent_id = uuid.uuid4()
        url = f'/api/v1/customers/{non_existent_id}/wallet/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data['error'])
        self.assertEqual(response.data['error_code'], 'CUSTOMER_NOT_FOUND')
    
    def test_list_merchant_wallets_success(self):
        """Test successful merchant wallets listing"""
        url = f'/api/v1/merchants/{self.merchant1.merchant_id}/wallets/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Check pagination data
        pagination = response.data['data']['pagination']
        self.assertEqual(pagination['total_count'], 1)  # Only active wallets by default
        self.assertEqual(pagination['current_page'], 1)
        
        # Check wallet data
        wallets = response.data['data']['wallets']
        self.assertEqual(len(wallets), 1)
        self.assertEqual(wallets[0]['wallet_id'], str(self.wallet1.wallet_id))
    
    def test_list_merchant_wallets_all_statuses(self):
        """Test merchant wallets listing with all statuses"""
        url = f'/api/v1/merchants/{self.merchant1.merchant_id}/wallets/?status=all'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include both active and frozen wallets
        pagination = response.data['data']['pagination']
        self.assertEqual(pagination['total_count'], 2)
        
        wallets = response.data['data']['wallets']
        self.assertEqual(len(wallets), 2)
    
    def test_list_merchant_wallets_filtered_by_name(self):
        """Test merchant wallets listing filtered by customer name"""
        url = f'/api/v1/merchants/{self.merchant1.merchant_id}/wallets/?status=all&customer_name=john'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only include John's wallet
        pagination = response.data['data']['pagination']
        self.assertEqual(pagination['total_count'], 1)
        
        wallets = response.data['data']['wallets']
        self.assertEqual(len(wallets), 1)
        self.assertEqual(wallets[0]['customer_name'], 'John')
    
    def test_list_merchant_wallets_wrong_merchant(self):
        """Test error when trying to access another merchant's wallets"""
        url = f'/api/v1/merchants/{self.merchant2.merchant_id}/wallets/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(response.data['error'])
        self.assertEqual(response.data['error_code'], 'PERMISSION_DENIED')
    
    def test_verify_data_integrity_success(self):
        """Test data integrity verification"""
        url = f'/api/v1/merchants/{self.merchant1.merchant_id}/integrity/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Check integrity report
        report = response.data['integrity_report']
        self.assertEqual(report['merchant_id'], str(self.merchant1.merchant_id))
        self.assertEqual(report['checks']['customers_count'], 2)
        self.assertEqual(report['checks']['wallets_count'], 2)
        self.assertEqual(report['checks']['customers_without_wallets'], 0)
        
        # Should be healthy since all customers have wallets
        self.assertTrue(report['summary']['healthy'])
    
    def test_verify_data_integrity_with_issues(self):
        """Test data integrity verification when there are issues"""
        # Create customer without wallet
        customer_no_wallet = Customer.objects.create(
            merchant=self.merchant1,
            first_name='NoWallet',
            last_name='Customer',
            phone_number='+26771234570',
            email='nowallet@test.com'
        )
        
        url = f'/api/v1/merchants/{self.merchant1.merchant_id}/integrity/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check integrity report shows issues
        report = response.data['integrity_report']
        self.assertEqual(report['checks']['customers_without_wallets'], 1)
        self.assertFalse(report['summary']['healthy'])
        self.assertEqual(report['summary']['issues_count'], 1)
        
        # Check issue details
        issues = report['issues']
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['type'], 'customers_without_wallets')
    
    def test_unauthenticated_requests(self):
        """Test that all endpoints require authentication"""
        endpoints = [
            f'/api/v1/customers/{self.customer1.customer_id}/wallet/',
            f'/api/v1/merchants/{self.merchant1.merchant_id}/wallets/',
            f'/api/v1/merchants/{self.merchant1.merchant_id}/integrity/',
        ]
        
        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_pagination_limits(self):
        """Test pagination limits and parameters"""
        url = f'/api/v1/merchants/{self.merchant1.merchant_id}/wallets/?page_size=1&status=all'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        pagination = response.data['data']['pagination']
        self.assertEqual(pagination['page_size'], 1)
        self.assertEqual(pagination['page_count'], 2)  # 2 wallets, 1 per page
        self.assertTrue(pagination['has_next'])
        self.assertFalse(pagination['has_previous'])