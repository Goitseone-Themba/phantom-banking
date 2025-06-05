import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import secrets
import string


class QRCode(models.Model):
    """QR Code for payment requests"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    reference = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255, blank=True)
    
    # QR Code specifics
    qr_token = models.CharField(max_length=32, unique=True, editable=False)
    qr_data = models.TextField()  # JSON string with payment data
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Payment tracking
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'qr_codes'
        indexes = [
            models.Index(fields=['qr_token']),
            models.Index(fields=['merchant', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.qr_token:
            self.qr_token = self.generate_token()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def generate_token(self):
        """Generate unique QR token"""
        while True:
            token = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
            if not QRCode.objects.filter(qr_token=token).exists():
                return token
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return self.status == 'active' and not self.is_expired
    
    def __str__(self):
        return f"QR-{self.qr_token} - P{self.amount}"


class EFTPayment(models.Model):
    """EFT Payment processing"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    BANK_CHOICES = [
        ('fnb', 'First National Bank'),
        ('standard', 'Standard Bank'),
        ('barclays', 'Barclays Bank'),
        ('nedbank', 'Nedbank'),
        ('choppies', 'Choppies Bank'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE)
    
    # EFT Details
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    bank_code = models.CharField(max_length=20, choices=BANK_CHOICES)
    account_number = models.CharField(max_length=50)
    reference = models.CharField(max_length=100)
    
    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_reference = models.CharField(max_length=100, blank=True, null=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Associated transaction
    transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'eft_payments'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['external_reference']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"EFT-{self.bank_code}-{self.amount}"


class Transaction(models.Model):
    """Enhanced transaction model"""
    TYPE_CHOICES = [
        ('qr_payment', 'QR Code Payment'),
        ('eft_topup', 'EFT Top-up'),
        ('wallet_transfer', 'Wallet Transfer'),
        ('merchant_payment', 'Merchant Payment'),
        ('refund', 'Refund'),
        ('fee', 'Transaction Fee'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core transaction data
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Parties involved
    from_wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, related_name='outgoing_transactions', null=True, blank=True)
    to_wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, related_name='incoming_transactions', null=True, blank=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, null=True, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['merchant', 'status']),
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Calculate net amount if not set
        if not self.net_amount:
            self.net_amount = self.amount - self.fee
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_type} - P{self.amount} - {self.status}"