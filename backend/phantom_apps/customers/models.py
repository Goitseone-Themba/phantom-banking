
import uuid
from django.db import models
from django.core.validators import RegexValidator


class Customer(models.Model):
    """Customer model for the banking system"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    
    # Contact information
    phone_number = models.CharField(
        max_length=15, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^7[0-9]{7}$',
                message='Phone number must be in format: 7XXXXXXX (Botswana format)'
            )
        ],
        help_text='Botswana phone number (e.g., 71234567)'
    )
    
    # Personal information
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name or self.phone_number}"
    
    @property
    def display_name(self):
        """Get display name for customer"""
        return self.full_name or f"Customer {self.phone_number}"
    
    def get_total_wallet_balance(self):
        """Get total balance across all wallets"""
        from phantom_apps.wallets.models import Wallet
        total = Wallet.objects.filter(customer=self).aggregate(
            total=models.Sum('balance')
        )['total']
        return total or 0