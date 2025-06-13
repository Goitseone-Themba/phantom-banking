# backend/phantom_apps/kyc/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import KYCRecord, KYCEvent
from .services.veriff_service import VeriffService
import json

class KYCModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_kyc_record_creation(self):
        kyc_record = KYCRecord.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            nationality='BW',
            document_type='passport',
            document_number='BP123456789',
            address_line_1='123 Main St',
            city='Gaborone',
            state_province='South East',
            postal_code='00000',
            country='BW'
        )
        
        self.assertEqual(kyc_record.user, self.user)
        self.assertEqual(kyc_record.status, KYCRecord.Status.PENDING)
        self.assertFalse(kyc_record.is_verified)
        self.assertFalse(kyc_record.is_expired)

    def test_kyc_approval(self):
        kyc_record = KYCRecord.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            nationality='BW',
            document_type='passport',
            document_number='BP123456789',
            address_line_1='123 Main St',
            city='Gaborone',
            state_province='South East',
            postal_code='00000',
            country='BW'
        )
        
        kyc_record.approve()
        self.assertEqual(kyc_record.status, KYCRecord.Status.APPROVED)
        self.assertTrue(kyc_record.is_verified)
        self.assertIsNotNone(kyc_record.verified_at)
        self.assertIsNotNone(kyc_record.expires_at)


class KYCAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_kyc_summary_no_record(self):
        url = reverse('kyc-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['kyc_status'], 'not_started')
        self.assertFalse(response.data['is_verified'])

    def test_kyc_summary_with_record(self):
        KYCRecord.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            nationality='BW',
            document_type='passport',
            document_number='BP123456789',
            address_line_1='123 Main St',
            city='Gaborone',
            state_province='South East',
            postal_code='00000',
            country='BW',
            status=KYCRecord.Status.APPROVED
        )
        
        url = reverse('kyc-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['kyc_status'], 'approved')
        self.assertTrue(response.data['is_verified'])

    @patch('phantom_apps.kyc.services.veriff_service.VeriffService.create_verification_session')
    def test_start_verification(self, mock_create_session):
        mock_create_session.return_value = (True, {
            'session_url': 'https://veriff.com/session/123',
            'session_id': 'session_123'
        })
        
        url = reverse('kyc-records-start-verification')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'nationality': 'BW',
            'document_type': 'passport',
            'document_number': 'BP123456789',
            'address_line_1': '123 Main St',
            'city': 'Gaborone',
            'state_province': 'South East',
            'postal_code': '00000',
            'country': 'BW'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('session_url', response.data)
        self.assertTrue(KYCRecord.objects.filter(user=self.user).exists())

    def test_start_verification_invalid_data(self):
        url = reverse('kyc-records-start-verification')
        data = {
            'first_name': '',  # Invalid: empty name
            'date_of_birth': '2010-01-01',  # Invalid: too young
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VeriffServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.kyc_record = KYCRecord.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            nationality='BW',
            document_type='passport',
            document_number='BP123456789',
            address_line_1='123 Main St',
            city='Gaborone',
            state_province='South East',
            postal_code='00000',
            country='BW'
        )
        self.service = VeriffService()

    @patch('phantom_apps.kyc.services.veriff_service.requests.post')
    def test_create_verification_session_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'verification': {
                'id': 'session_123',
                'url': 'https://veriff.com/session/123'
            }
        }
        mock_post.return_value = mock_response
        
        success, result = self.service.create_verification_session(self.kyc_record)
        
        self.assertTrue(success)
        self.assertIn('session_url', result)
        self.kyc_record.refresh_from_db()
        self.assertEqual(self.kyc_record.veriff_session_id, 'session_123')

    @patch('phantom_apps.kyc.services.veriff_service.requests.post')
    def test_create_verification_session_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        success, result = self.service.create_verification_session(self.kyc_record)
        
        self.assertFalse(success)
        self.assertIn('error', result)

    def test_handle_webhook_approved(self):
        self.kyc_record.veriff_session_id = 'session_123'
        self.kyc_record.save()
        
        webhook_payload = {
            'id': 'session_123',
            'verification': {
                'decision': 'approved',
                'code': '9001',
                'reason': None
            }
        }
        
        result = self.service.handle_webhook(webhook_payload, 'test_signature')
        
        self.assertTrue(result)
        self.kyc_record.refresh_from_db()
        self.assertEqual(self.kyc_record.status, KYCRecord.Status.APPROVED)
        self.assertEqual(self.kyc_record.veriff_decision, 'approved')

    def test_handle_webhook_rejected(self):
        self.kyc_record.veriff_session_id = 'session_123'
        self.kyc_record.save()
        
        webhook_payload = {
            'id': 'session_123',
            'verification': {
                'decision': 'declined',
                'code': '9102',
                'reason': 'Document quality too low'
            }
        }
        
        result = self.service.handle_webhook(webhook_payload, 'test_signature')
        
        self.assertTrue(result)
        self.kyc_record.refresh_from_db()
        self.assertEqual(self.kyc_record.status, KYCRecord.Status.REJECTED)
        self.assertEqual(self.kyc_record.veriff_decision, 'declined')


# CSS Styles for Frontend Components
# frontend/src/components/KYC/KYC.css

CSS_STYLES = """
/* KYC Component Styles */

.kyc-verification {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.kyc-status {
  text-align: center;
  padding: 40px 20px;
}

.status-verified {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border: 1px solid #c3e6cb;
  border-radius: 12px;
  padding: 30px;
  color: #155724;
}

.status-pending {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border: 1px solid #ffeaa7;
  border-radius: 12px;
  padding: 30px;
  color: #856404;
}

.status-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.wallet-info {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
}

.kyc-form {
  background: #ffffff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 8px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #34495e;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9, #21618c);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-refresh {
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  color: #495057;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-refresh:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 6px;
  margin: 20px 0;
  border: 1px solid #f5c6cb;
}

.kyc-processing {
  text-align: center;
  padding: 60px 20px;
}

.processing-animation {
  font-size: 4rem;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* KYC Dashboard Styles */

.kyc-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-layout {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 30px;
  margin-top: 20px;
}

.records-list {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.record-item {
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.record-item:hover {
  border-color: #3498db;
  background: #f8f9ff;
}

.record-item.selected {
  border-color: #3498db;
  background: #e3f2fd;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.user-name {
  font-weight: 600;
  color: #2c3e50;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.record-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.record-details small {
  color: #6c757d;
  font-size: 12px;
}

.record-details-panel {
  background: #ffffff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-item label {
  font-weight: 600;
  color: #6c757d;
  font-size: 14px;
}

.detail-item span {
  color: #2c3e50;
  font-size: 16px;
}

.events-section {
  border-top: 1px solid #dee2e6;
  padding-top: 20px;
}

.event-item {
  background: #f8f9fa;
  border-left: 4px solid #3498db;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 0 6px 6px 0;
}

.event-type {
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  font-size: 12px;
  margin-bottom: 5px;
}

.event-description {
  color: #495057;
  margin-bottom: 8px;
}

.event-timestamp {
  font-size: 12px;
  color: #6c757d;
}

.event-user {
  font-style: italic;
}

/* Responsive Design */

@media (max-width: 768px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .kyc-verification {
    padding: 10px;
  }
}
"""

# Test Data Factory
# backend/phantom_apps/kyc/factories.py

TEST_FACTORY = '''
import factory
from django.contrib.auth.models import User
from .models import KYCRecord, KYCEvent, KYCDocument

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

class KYCRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KYCRecord
    
    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    nationality = "BW"
    document_type = "passport"
    document_number = factory.Faker("bothify", text="BP########")
    address_line_1 = factory.Faker("street_address")
    city = factory.Faker("city")
    state_province = factory.Faker("state")
    postal_code = factory.Faker("postcode")
    country = "BW"
    status = KYCRecord.Status.PENDING

class KYCEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KYCEvent
    
    kyc_record = factory.SubFactory(KYCRecordFactory)
    event_type = KYCEvent.EventType.SESSION_CREATED
    description = factory.Faker("sentence")
    metadata = factory.Dict({})
'''