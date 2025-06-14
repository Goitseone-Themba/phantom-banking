from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class Wallet(models.Model):
    """Independent phantom wallet model - no longer tied to specific merchant"""
    
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE, related_name='wallet')
    
    # Balance and currency
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='BWP')
    
    # Limits (consolidated - removed duplicate fields)
    daily_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('50000.00'))
    monthly_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('200000.00'))
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    is_frozen = models.BooleanField(default=False)

    # KYC-related fields
    is_kyc_verified = models.BooleanField(default=False)
    wallet_type = models.CharField(max_length=20, default='basic')  # basic, verified, premium
    upgraded_at = models.DateTimeField(null=True, blank=True)
    
    # Wallet creation metadata
    created_by_merchant = models.ForeignKey(
        'merchants.Merchant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_wallets',
        help_text="Merchant who initially created this wallet"
    )
    
    class Meta:
        db_table = 'wallets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by_merchant']),
        ]
    
    def __str__(self):
        return f"Wallet {self.wallet_id} - {self.customer.first_name} {self.customer.last_name}"
    
    def get_accessible_merchants(self):
        """Get all merchants that have access to this wallet"""
        from ..customers.models import MerchantCustomerAccess
        return MerchantCustomerAccess.objects.filter(
            customer=self.customer,
            is_active=True
        ).select_related('merchant')
    
    def merchant_has_access(self, merchant, access_type='view_only'):
        """Check if a merchant has specific access to this wallet"""
        from ..customers.models import MerchantCustomerAccess
        
        access_hierarchy = {
            'view_only': ['view_only', 'credit_only', 'full'],
            'credit_only': ['credit_only', 'full'],
            'full': ['full']
        }
        
        try:
            access = MerchantCustomerAccess.objects.get(
                merchant=merchant,
                customer=self.customer,
                is_active=True
            )
            return access.is_valid and access.access_type in access_hierarchy.get(access_type, [])
        except MerchantCustomerAccess.DoesNotExist:
            return False
