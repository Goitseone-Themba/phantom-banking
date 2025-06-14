"""
Merchant component tests
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from phantom_apps.merchants.models import Merchant, APICredential

def test_merchant_creation():
    """Test merchant model creation"""
    print("🧪 Testing merchant creation...")
    
    try:
        # Create test user
        user = User.objects.create_user(
            username='testmerchant',
            email='test@merchant.com',
            password='testpass123'
        )
        
        # Create merchant
        merchant = Merchant.objects.create(
            user=user,
            business_name='Test Business',
            fnb_account_number='1234567890',
            contact_email='test@merchant.com',
            phone_number='+26771234567',
            business_registration='TEST123'
        )
        
        assert merchant.merchant_id is not None
        assert merchant.business_name == 'Test Business'
        assert merchant.is_active == True
        
        print("✅ Merchant creation test passed")
        
        # Clean up
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Merchant creation test failed: {e}")
        return False

def test_api_credential_creation():
    """Test API credential creation"""
    print("🧪 Testing API credential creation...")
    
    try:
        # Create test user and merchant
        user = User.objects.create_user(
            username='testmerchant2',
            email='test2@merchant.com',
            password='testpass123'
        )
        
        merchant = Merchant.objects.create(
            user=user,
            business_name='Test Business 2',
            fnb_account_number='1234567891',
            contact_email='test2@merchant.com',
            phone_number='+26771234568',
            business_registration='TEST124'
        )
        
        # Create API credential
        api_cred = APICredential.objects.create(
            merchant=merchant,
            api_key='test_api_key_123',
            api_secret_hash='hashed_secret',
            permissions=['read', 'write']
        )
        
        assert api_cred.credential_id is not None
        assert api_cred.api_key == 'test_api_key_123'
        assert api_cred.is_active == True
        
        print("✅ API credential creation test passed")
        
        # Clean up
        api_cred.delete()
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ API credential creation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏦 Testing Merchant Components")
    print("=" * 40)
    
    tests = [
        test_merchant_creation,
        test_api_credential_creation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Merchant Tests: {passed}/{len(tests)} passed")
