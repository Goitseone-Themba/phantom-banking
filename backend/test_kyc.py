from django.contrib.auth.models import User
from phantom_apps.kyc.models import KYCRecord
from phantom_apps.kyc.services.veriff_service import VeriffService

# Create test user
user = User.objects.create_user('testuser', 'test@example.com', 'password')

# Start KYC process
kyc_data = {
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

kyc_record = KYCRecord.objects.create(user=user, **kyc_data)
veriff_service = VeriffService()
success, result = veriff_service.create_verification_session(kyc_record)
print(f"Session created: {success}")
print(f"Session URL: {result.get('session_url')}")