import uuid
from django.db import models
from django.core.validators import EmailValidator


class Merchant(models.Model):
    """Merchant model for businesses accepting payments"""
    
    BUSINESS_TYPES = [
        ('retail', 'Retail Store'),
        ('restaurant', 'Restaurant'),
        ('service', 'Service Provider'),
        ('online', 'Online Business'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Business information
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES, default='retail')
    business_registration = models.CharField(max_length=50, blank=True, null=True)
    
    # Contact information
    contact_email = models.EmailField(validators=[EmailValidator()])
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    
    # Business settings
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0.0250,
        help_text='Commission rate as decimal (e.g., 0.0250 for 2.5%)'
    )
    
    # Status and verification
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'merchants'
        indexes = [
            models.Index(fields=['business_name']),
            models.Index(fields=['contact_email']),
            models.Index(fields=['business_type']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['business_name']
    
    def __str__(self):
        return self.business_name
    
    def get_total_revenue(self):
        """Get total revenue from all transactions"""
        from phantom_apps.transactions.models import Transaction
        total = Transaction.objects.filter(
            merchant=self,
            status='completed'
        ).aggregate(total=models.Sum('amount'))['total']
        return total or 0
    
    def get_transaction_count(self):
        """Get total number of transactions"""
        from phantom_apps.transactions.models import Transaction
        return Transaction.objects.filter(
            merchant=self,
            status='completed'
        ).count()