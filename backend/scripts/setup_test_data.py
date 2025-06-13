"""
Setup test data for Wallet API testing
"""
import os
import sys
import django
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from phantom_apps.merchants.models import Merchant
from phantom_apps.customers.models import Customer
from rest_framework_simplejwt.tokens import RefreshToken

def setup_test_data():
    """Create test data for API testing"""
    print("🏗️ Setting up test data...")
    
    # Create or get merchant user
    user, created = User.objects.get_or_create(
        username='testmerchant',
        defaults={
            'email': 'test@merchant.com',
            'password': 'testpass123'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Create or get merchant
    merchant, created = Merchant.objects.get_or_create(
        user=user,
        defaults={
            'business_name': 'Test Business',
            'fnb_account_number': '1234567890',
            'contact_email': 'test@merchant.com',
            'phone_number': '+26771234567',
            'business_registration': 'TEST123'
        }
    )
    
    if created:
        print("✅ Created test merchant")
    else:
        print("✅ Using existing test merchant")
    
    # Create or get customer
    customer, created = Customer.objects.get_or_create(
        phone_number='+26771234568',
        merchant=merchant,
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'identity_number': '123456789'
        }
    )
    
    if created:
        print("✅ Created test customer")
    else:
        print("✅ Using existing test customer")
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print("\n🔑 Test Data Ready!")
    print(f"Customer ID: {customer.customer_id}")
    print(f"JWT Token: {access_token}")
    print(f"\n📝 Test URL:")
    print(f"POST http://localhost:8000/api/v1/merchants/me/customers/{customer.customer_id}/wallet/")
    print(f"\n🔐 Authorization Header:")
    print(f"Authorization: Bearer {access_token}")
    
    return {
        'customer_id': customer.customer_id,
        'jwt_token': access_token,
        'user': user,
        'merchant': merchant,
        'customer': customer
    }

if __name__ == "__main__":
    setup_test_data()