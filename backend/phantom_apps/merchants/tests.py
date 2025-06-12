from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Merchant, APICredential
from django.urls import reverse

User = get_user_model()

class MerchantModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='libby',
            password='testpass123',
            email='libbygare@gmail.com'
        )
        self.merchant = Merchant.objects.create(
            user=self.user,
            business_name='MySpar',
            fnb_account_number='1234567890',
            contact_email='libbygare@gmail.com',
            phone_number='+1234567890',
            business_registration='REG123456',
            commission_rate=0.5
        )

    def test_merchant_creation(self):
        self.assertEqual(self.merchant.business_name, 'MySpar')
        self.assertEqual(self.merchant.user, self.user)
        self.assertTrue(self.merchant.is_active)

class MerchantAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='lebang',
            password='testpass123',
            email='libbygare@gmail.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.merchant_data = {
            'business_name': '',
            'fnb_account_number': '1234567890',
            'contact_email': 'lebanggarebantsi@gmail',
            'phone_number': '+1234567890',
            'business_registration': 'REG123456',
            'commission_rate': 0.5
        }

    def test_create_merchant(self):
        url = reverse('merchant-list')
        response = self.client.post(url, self.merchant_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Merchant.objects.count(), 1)
        self.assertEqual(Merchant.objects.get().business_name, 'Choppies')

    def test_get_merchant_list(self):
        Merchant.objects.create(user=self.user, **self.merchant_data)
        url = reverse('merchant-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)