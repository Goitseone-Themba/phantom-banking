"""
Wallet component tests
"""
import os
import sys
import django
from pathlib import Path
from decimal import Decimal

# Setup Django
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from phantom_apps.merchants.models import Merchant
from phantom_apps.customers.models import Customer
from phantom_apps.wallets.models import Wallet

def test_wallet_creation():
    """Test wallet model creation"""
    print("🧪 Testing wallet creation...")
    
    try:
        # Create test data
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
        
        customer = Customer.objects.create(
            merchant=merchant,
            first_name='John',
            last_name='Doe',
            phone_number='+26771234569',
            email='john@example.com'
        )
        
        # Create wallet
        wallet = Wallet.objects.create(
            customer=customer,
            merchant=merchant,
            balance=Decimal('100.00'),
            currency='BWP'
        )
        
        assert wallet.wallet_id is not None
        assert wallet.balance == Decimal('100.00')
        assert wallet.currency == 'BWP'
        assert wallet.status == 'active'
        assert wallet.is_frozen == False
        
        print("✅ Wallet creation test passed")
        
        # Clean up
        wallet.delete()
        customer.delete()
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Wallet creation test failed: {e}")
        return False

def test_wallet_relationships():
    """Test wallet relationships"""
    print("🧪 Testing wallet relationships...")
    
    try:
        # Create test data
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
        
        customer = Customer.objects.create(
            merchant=merchant,
            first_name='Jane',
            last_name='Smith',
            phone_number='+26771234570',
            email='jane@example.com'
        )
        
        # Create wallet
        wallet = Wallet.objects.create(
            customer=customer,
            merchant=merchant,
            balance=Decimal('500.00')
        )
        
        # Test relationships
        assert wallet.customer == customer
        assert wallet.merchant == merchant
        assert customer.wallet == wallet
        assert wallet in merchant.wallets.all()
        
        print("✅ Wallet relationships test passed")
        
        # Clean up
        wallet.delete()
        customer.delete()
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Wallet relationships test failed: {e}")
        return False

if __name__ == "__main__":
    print("💰 Testing Wallet Components")
    print("=" * 40)
    
    tests = [
        test_wallet_creation,
        test_wallet_relationships
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Wallet Tests: {passed}/{len(tests)} passed")