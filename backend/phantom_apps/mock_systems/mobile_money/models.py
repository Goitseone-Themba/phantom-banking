from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class MockMobileMoneyAccount(models.Model):
    """Mock mobile money account for development"""
    
    PROVIDERS = [
        ('orange', 'Orange Money'),
        ('mascom', 'Mascom MyZaka'),
        ('btc', 'BTC Smega'),
    ]
    
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True)
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Account status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mock_mobile_money_accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.phone_number}"
