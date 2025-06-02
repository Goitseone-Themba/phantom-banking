from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class Transaction(models.Model):
    """Transaction model for all payment operations"""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('transfer', 'Transfer'),
    ]
    
    PAYMENT_CHANNELS = [
        ('qr_code', 'QR Code'),
        ('eft', 'EFT'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, related_name='transactions')
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BWP')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    payment_channel = models.CharField(max_length=20, choices=PAYMENT_CHANNELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # References and descriptions
    reference_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    external_reference = models.CharField(max_length=100, blank=True)
    
    # Fees and reconciliation
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_reconciled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Failure information
    failure_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['merchant', 'created_at']),
            models.Index(fields=['wallet', 'created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.reference_number} - {self.amount} {self.currency}"
