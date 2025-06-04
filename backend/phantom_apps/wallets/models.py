from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

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
    merchant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='merchant_wallets')
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
        db_table = 'wallets'