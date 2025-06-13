from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Merchant(models.Model):
    """Merchant model for businesses using Phantom Banking"""
    
    merchant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant')
    business_name = models.CharField(max_length=255)
    fnb_account_number = models.CharField(max_length=20, unique=True)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    business_registration = models.CharField(max_length=50, unique=True)
    
    # API credentials
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    api_secret_hash = models.CharField(max_length=128, blank=True)
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Business settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.50)
    webhook_url = models.URLField(blank=True, null=True)
    
    class Meta:
        db_table = 'merchants'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.business_name

class APICredential(models.Model):
    """API credentials for merchant authentication"""
    
    credential_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='credentials')
    api_key = models.CharField(max_length=64, unique=True)
    api_secret_hash = models.CharField(max_length=128)
    permissions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_credentials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.api_key[:8]}..."
