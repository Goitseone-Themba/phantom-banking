import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class Wallet(models.Model):
    """Wallet model for customer balances per merchant"""
    
    WALLET_TYPES = [
        ('standard', 'Standard Wallet'),
        ('premium', 'Premium Wallet'),
        ('business', 'Business Wallet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='wallets'
    )
    merchant = models.ForeignKey(
        'merchants.Merchant',
        on_delete=models.CASCADE,
        related_name='customer_wallets'
    )
    
    # Wallet details
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPES, default='standard')
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Limits
    daily_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('5000.00'),
        help_text='Daily transaction limit'
    )
    monthly_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('50000.00'),
        help_text='Monthly transaction limit'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_frozen = models.BooleanField(default=False)
    freeze_reason = models.CharField(max_length=255, blank=True, null=True)
    
    # Metadata
    currency = models.CharField(max_length=3, default='BWP')
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_transaction_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'wallets'
        unique_together = ['customer', 'merchant']
        indexes = [
            models.Index(fields=['customer', 'merchant']),
            models.Index(fields=['balance']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.display_name} - {self.merchant.business_name} (P{self.balance})"
    
    @property
    def formatted_balance(self):
        """Get formatted balance with currency"""
        return f"P{self.balance:,.2f}"
    
    def can_debit(self, amount):
        """Check if wallet can be debited with given amount"""
        if not self.is_active or self.is_frozen:
            return False, "Wallet is not active or frozen"
        
        if self.balance < amount:
            return False, "Insufficient balance"
        
        return True, "OK"
    
    def debit(self, amount, description=""):
        """Debit amount from wallet"""
        can_debit, message = self.can_debit(amount)
        if not can_debit:
            raise ValueError(message)
        
        self.balance -= amount
        self.save(update_fields=['balance', 'updated_at'])
        return self.balance
    
    def credit(self, amount, description=""):
        """Credit amount to wallet"""
        if not self.is_active:
            raise ValueError("Wallet is not active")
        
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])
        return self.balance
    
    def get_daily_spent(self, date=None):
        """Get amount spent today"""
        from django.utils import timezone
        from phantom_apps.transactions.models import Transaction
        
        if date is None:
            date = timezone.now().date()
        
        daily_spent = Transaction.objects.filter(
            from_wallet=self,
            status='completed',
            created_at__date=date
        ).aggregate(total=models.Sum('amount'))['total']
        
        return daily_spent or Decimal('0.00')
    
    def get_monthly_spent(self, year=None, month=None):
        """Get amount spent this month"""
        from django.utils import timezone
        from phantom_apps.transactions.models import Transaction
        
        if year is None or month is None:
            now = timezone.now()
            year = now.year
            month = now.month
        
        monthly_spent = Transaction.objects.filter(
            from_wallet=self,
            status='completed',
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=models.Sum('amount'))['total']
        
        return monthly_spent or Decimal('0.00')