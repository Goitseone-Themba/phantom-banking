from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class MockFNBAccount(models.Model):
    """Mock FNB account for development and testing"""
    
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_number = models.CharField(max_length=20, unique=True)
    account_holder_name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='BWP')
    
    # Account status
    is_active = models.BooleanField(default=True)
    account_type = models.CharField(max_length=20, default='savings')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mock_fnb_accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"FNB Account {self.account_number} - {self.account_holder_name}"

class MockFNBTransaction(models.Model):
    """Mock FNB transaction for testing"""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(MockFNBAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'mock_fnb_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"FNB Transaction {self.reference} - {self.amount}"
