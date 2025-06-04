from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class Wallet(models.Model):
    """Phantom wallet model"""
    
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE, related_name='wallet')
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='wallets')
    
    # Balance and currency
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='BWP')
    
    # Limits
    daily_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('50000.00'))
    monthly_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('200000.00'))
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    is_frozen = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'wallets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Wallet {self.wallet_id} - {self.customer.first_name} {self.customer.last_name}"