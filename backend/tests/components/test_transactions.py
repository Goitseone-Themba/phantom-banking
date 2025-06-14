"""
Transaction component tests
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
from phantom_apps.transactions.models import Transaction

def test_transaction_creation():
    """Test transaction model creation"""
    print("🧪 Testing transaction creation...")
    
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
        
        wallet = Wallet.objects.create(
            customer=customer,
            merchant=merchant,
            balance=Decimal('100.00')
        )
        
        # Create transaction
        transaction = Transaction.objects.create(
            wallet=wallet,
            merchant=merchant,
            amount=Decimal('50.00'),
            currency='BWP',
            transaction_type='credit',
            payment_channel='qr_code',
            reference_number='TXN001',
            description='Test transaction'
        )
        
        assert transaction.transaction_id is not None
        assert transaction.amount == Decimal('50.00')
        assert transaction.status == 'pending'
        assert transaction.transaction_type == 'credit'
        assert transaction.payment_channel == 'qr_code'
        
        print("✅ Transaction creation test passed")
        
        # Clean up
        transaction.delete()
        wallet.delete()
        customer.delete()
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Transaction creation test failed: {e}")
        return False

def test_transaction_relationships():
    """Test transaction relationships"""
    print("🧪 Testing transaction relationships...")
    
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
        
        wallet = Wallet.objects.create(
            customer=customer,
            merchant=merchant,
            balance=Decimal('200.00')
        )
        
        # Create multiple transactions
        transaction1 = Transaction.objects.create(
            wallet=wallet,
            merchant=merchant,
            amount=Decimal('25.00'),
            currency='BWP',
            transaction_type='debit',
            payment_channel='eft',
            reference_number='TXN002',
            description='Test debit'
        )
        
        transaction2 = Transaction.objects.create(
            wallet=wallet,
            merchant=merchant,
            amount=Decimal('75.00'),
            currency='BWP',
            transaction_type='credit',
            payment_channel='qr_code',
            reference_number='TXN003',
            description='Test credit'
        )
        
        # Test relationships
        assert transaction1.wallet == wallet
        assert transaction1.merchant == merchant
        assert transaction2.wallet == wallet
        assert transaction2.merchant == merchant
        assert wallet.transactions.count() == 2
        assert merchant.transactions.count() == 2
        
        print("✅ Transaction relationships test passed")
        
        # Clean up
        transaction1.delete()
        transaction2.delete()
        wallet.delete()
        customer.delete()
        merchant.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Transaction relationships test failed: {e}")
        return False

if __name__ == "__main__":
    print("💳 Testing Transaction Components")
    print("=" * 40)
    
    tests = [
        test_transaction_creation,
        test_transaction_relationships
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Transaction Tests: {passed}/{len(tests)} passed")