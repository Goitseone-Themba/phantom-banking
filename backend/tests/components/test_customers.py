"""
Customer component tests
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

from django.contrib.auth.models import User
from phantom_apps.merchants.models import Merchant
from phantom_apps.customers.models import Customer

def test_customer_creation():
    """Test customer model creation"""
    print("🧪 Testing customer creation...")
    
    try:
        # Create test merchant first
        user = User.objects.create_user(
            username='testmerchant',
            email='test@merchant.com',
            password='testpass123'
        )
        
        merchant = Merchant.objects.create(
            user=user,
            business_name='Test Business',
            fnb_account_number='1234567890',
            contact_email='test@merchant.com',
            phone_number='+26771234567',
            business_registration='TEST123'
        )
        
        # Create customer
        customer = Customer.objects.create(
            merchant=merchant,
            first_name='John',
            last_name='Doe',
            phone_number='+26771234569',
            email='john@example.com',
            identity_number='123456789'
        )
        
        assert customer.customer_id is not None
        assert customer.first_name == 'John'
        assert customer.status == 'active'
        assert str(customer) == 'John Doe'
        
        print("✅ Customer creation test passed")
        
        # Clean up
        customer.delete()
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Customer creation test failed: {e}")
        return False

def test_customer_merchant_relationship():
    """Test customer-merchant relationship"""
    print("🧪 Testing customer-merchant relationship...")
    
    try:
        # Create test merchant
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
        
        # Create multiple customers
        customer1 = Customer.objects.create(
            merchant=merchant,
            first_name='Jane',
            last_name='Smith',
            phone_number='+26771234570',
            email='jane@example.com'
        )
        
        customer2 = Customer.objects.create(
            merchant=merchant,
            first_name='Bob',
            last_name='Johnson',
            phone_number='+26771234571',
            email='bob@example.com'
        )
        
        # Test relationships
        assert customer1.merchant == merchant
        assert customer2.merchant == merchant
        assert merchant.customers.count() == 2
        
        print("✅ Customer-merchant relationship test passed")
        
        # Clean up
        customer1.delete()
        customer2.delete()
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Customer-merchant relationship test failed: {e}")
        return False

if __name__ == "__main__":
    print("👤 Testing Customer Components")
    print("=" * 40)
    
    tests = [
        test_customer_creation,
        test_customer_merchant_relationship
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Customer Tests: {passed}/{len(tests)} passed")