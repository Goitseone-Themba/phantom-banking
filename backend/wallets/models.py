from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

class WalletCreationRequest(models.Model):
    """Model to track wallet creation requests from trusted merchants"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='wallet_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Customer Details
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    national_id = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    username = models.CharField(max_length=150, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Wallet Request {self.request_id} - {self.first_name} {self.last_name}"
    
    def send_notification_email(self):
        """Send notification email to customer about wallet creation"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        context = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'merchant_name': self.merchant.business_name,
            'created_at': self.created_at,
            'status': self.status
        }
        
        html_message = render_to_string('email/wallet_creation.html', context)
        plain_message = strip_tags(html_message)
        
        subject = 'Your Wallet Request Status'
        if self.status == 'approved':
            subject = 'Your Wallet Has Been Created'
        elif self.status == 'rejected':
            subject = 'Your Wallet Request Has Been Declined'
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            html_message=html_message
        )

class Wallet(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('blocked', 'Blocked'),
        ('suspended', 'Suspended'),
    )

    WALLET_TYPE_CHOICES = (
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('fnb', 'FNB Account')
    )

    # Core Fields
    wallet_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='wallets')
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.PROTECT, related_name='wallets', null=True, default=None)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    
    # Status and Type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPE_CHOICES, default='basic')
    
    # Security and Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    last_transaction = models.DateTimeField(null=True, blank=True)
    last_balance_update = models.DateTimeField(auto_now=True)
    daily_transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('1000.00'))
    monthly_transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('10000.00'))
    
    # Tracking Fields
    daily_transaction_count = models.PositiveIntegerField(default=0)
    monthly_transaction_count = models.PositiveIntegerField(default=0)
    daily_transaction_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    monthly_transaction_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_block_wallet", "Can block wallet"),
            ("can_view_merchant_wallets", "Can view merchant wallets"),
            ("can_manage_transaction_limits", "Can manage transaction limits"),
        ]

    def __str__(self):
        return f"{self.wallet_id} - {self.user.username}"
        
    def save(self, *args, **kwargs):
        if not self.wallet_id:
            self.wallet_id = f"W{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def is_transaction_allowed(self, amount):
        if self.status != 'active':
            return False, "Wallet is not active"
            
        if amount > self.balance:
            return False, "Insufficient funds"
            
        if (self.daily_transaction_amount + amount) > self.daily_transaction_limit:
            return False, "Daily transaction limit exceeded"
            
        if (self.monthly_transaction_amount + amount) > self.monthly_transaction_limit:
            return False, "Monthly transaction limit exceeded"
            
        return True, "Transaction allowed"

class WalletAuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('block', 'Block'),
        ('unblock', 'Unblock'),
        ('limit_change', 'Limit Change'),
        ('type_change', 'Type Change'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()
    ip_address = models.GenericIPAddressField()

    class Meta:
        ordering = ['-timestamp']