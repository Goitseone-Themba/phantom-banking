"""
Mock systems component tests
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

from phantom_apps.mock_systems.fnb.models import MockFNBAccount, MockFNBTransaction
from phantom_apps.mock_systems.mobile_money.models import MockMobileMoneyAccount

def test_mock_fnb_account():
    """Test mock FNB account creation"""
    print("🧪 Testing mock FNB account creation...")
    
    try:
        account = MockFNBAccount.objects.create(
            account_number='1234567890',
            account_holder_name='John Doe',
            balance=Decimal('1000.00'),
            currency='BWP'
        )
        
        assert account.account_id is not None
        assert account.account_number == '1234567890'
        assert account.balance == Decimal('1000.00')
        assert account.is_active == True
        
        print("✅ Mock FNB account creation test passed")
        
        # Clean up
        account.delete()
        return True
        
    except Exception as e:
        print(f"❌ Mock FNB account creation test failed: {e}")
        return False

def test_mock_fnb_transaction():
    """Test mock FNB transaction creation"""
    print("🧪 Testing mock FNB transaction creation...")
    
    try:
        account = MockFNBAccount.objects.create(
            account_number='1234567891',
            account_holder_name='Jane Smith',
            balance=Decimal('500.00')
        )
        
        transaction = MockFNBTransaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            transaction_type='credit',
            reference='REF001',
            description='Test transaction'
        )
        
        assert transaction.transaction_id is not None
        assert transaction.amount == Decimal('100.00')
        assert transaction.transaction_type == 'credit'
        assert transaction.account == account
        
        print("✅ Mock FNB transaction creation test passed")
        
        # Clean up
        transaction.delete()
        account.delete()
        return True
        
    except Exception as e:
        print(f"❌ Mock FNB transaction creation test failed: {e}")
        return False

def test_mock_mobile_money_account():
    """Test mock mobile money account creation"""
    print("🧪 Testing mock mobile money account creation...")
    
    try:
        account = MockMobileMoneyAccount.objects.create(
            phone_number='+26771234567',
            provider='orange',
            balance=Decimal('250.00')
        )
        
        assert account.account_id is not None
        assert account.phone_number == '+26771234567'
        assert account.provider == 'orange'
        assert account.balance == Decimal('250.00')
        assert account.is_active == True
        
        print("✅ Mock mobile money account creation test passed")
        
        # Clean up
        account.delete()
        return True
        
    except Exception as e:
        print(f"❌ Mock mobile money account creation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Testing Mock Systems Components")
    print("=" * 40)
    
    tests = [
        test_mock_fnb_account,
        test_mock_fnb_transaction,
        test_mock_mobile_money_account
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Mock Systems Tests: {passed}/{len(tests)} passed")
