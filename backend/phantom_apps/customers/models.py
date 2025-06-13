from django.db import models
from django.utils import timezone
import uuid

class Customer(models.Model):
    """Customer model for phantom wallet users"""
    
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='customers')
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    identity_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    is_verified = models.BooleanField(default=False)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    nationality = models.CharField(max_length=50, default='BW')
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        unique_together = ['merchant', 'phone_number']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
