from django.db import models
from django.utils import timezone
import uuid

class Customer(models.Model):
    """Customer model for phantom wallet users - Independent across merchants"""
    
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)  # Global unique phone number
    email = models.EmailField(blank=True, null=True)
    identity_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    is_verified = models.BooleanField(default=False)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    nationality = models.CharField(max_length=50, default='BW')
    
    # Wallet creation tracking
    wallet_created_by = models.ForeignKey(
        'merchants.Merchant', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_customers',
        help_text="Merchant who initially created this customer's wallet"
    )
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['identity_number']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class MerchantCustomerAccess(models.Model):
    """Admin-controlled access permissions for merchants to customer wallets"""
    
    ACCESS_TYPES = [
        ('full', 'Full Access - Can debit and credit'),
        ('credit_only', 'Credit Only - Can only add funds'),
        ('view_only', 'View Only - Can view balance only'),
        ('suspended', 'Suspended - No access (admin action)'),
    ]
    
    GRANT_REASONS = [
        ('wallet_creation', 'Wallet Creation - Automatic access for wallet creator'),
        ('business_partnership', 'Business Partnership - Admin approved partnership'),
        ('customer_request', 'Customer Request - Customer requested merchant access'),
        ('admin_grant', 'Admin Grant - Manual admin approval'),
        ('api_integration', 'API Integration - Technical integration approval'),
    ]
    
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='customer_access')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='merchant_access')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES, default='full')
    grant_reason = models.CharField(max_length=30, choices=GRANT_REASONS, default='wallet_creation')
    
    # Admin-controlled metadata
    granted_at = models.DateTimeField(default=timezone.now)
    # Note: Admin tracking fields will be added later via admin interface actions
    created_by_merchant = models.ForeignKey(
        'merchants.Merchant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auto_granted_access',
        help_text="Merchant who created the wallet (auto-granted access)"
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Admin audit fields (simplified for now)
    last_modified_at = models.DateTimeField(auto_now=True)
    suspension_reason = models.TextField(blank=True, help_text="Reason for suspension (admin use)")
    
    class Meta:
        db_table = 'merchant_customer_access'
        unique_together = ['merchant', 'customer']
        indexes = [
            models.Index(fields=['merchant', 'customer']),
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.merchant.business_name} -> {self.customer} ({self.access_type})"
    
    @property
    def is_valid(self):
        """Check if access is currently valid"""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
