import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings

class Merchant(models.Model):
    merchant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(max_length=255)
    fnb_account_number = models.CharField(max_length=20, unique=True)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    business_registration = models.CharField(max_length=50, unique=True)
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    api_secret_hash = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.5)
    webhook_url = models.URLField(null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='merchant')

    class Meta:
        db_table = 'merchants'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} ({self.merchant_id})"


class APICredential(models.Model):
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
        return f"API Credential {self.credential_id} for {self.merchant.business_name}"