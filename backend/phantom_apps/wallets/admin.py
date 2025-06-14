from django.contrib import admin
from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin interface for Wallet model"""
    
    list_display = [
        'wallet_id',
        'customer',
        'created_by_merchant',
        'balance',
        'currency',
        'wallet_type',
        'status',
        'is_frozen',
        'is_kyc_verified',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'is_frozen',
        'is_kyc_verified',
        'wallet_type',
        'currency',
        'created_by_merchant',
        'created_at',
    ]
    
    search_fields = [
        'wallet_id',
        'customer__first_name',
        'customer__last_name',
        'customer__email',
        'customer__phone_number',
    ]
    
    readonly_fields = [
        'wallet_id',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'wallet_id',
                'customer',
                'created_by_merchant',
                'status',
                'is_frozen',
            )
        }),
        ('Balance & Currency', {
            'fields': (
                'balance',
                'currency',
            )
        }),
        ('Limits & KYC', {
            'fields': (
                'wallet_type',
                'is_kyc_verified',
                'daily_limit',
                'monthly_limit',
                'upgraded_at',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    # Add actions
    actions = ['freeze_wallets', 'unfreeze_wallets', 'mark_kyc_verified']
    
    def freeze_wallets(self, request, queryset):
        """Freeze selected wallets"""
        updated = queryset.update(is_frozen=True)
        self.message_user(
            request, 
            f'{updated} wallet(s) were successfully frozen.'
        )
    freeze_wallets.short_description = "Freeze selected wallets"
    
    def unfreeze_wallets(self, request, queryset):
        """Unfreeze selected wallets"""
        updated = queryset.update(is_frozen=False)
        self.message_user(
            request, 
            f'{updated} wallet(s) were successfully unfrozen.'
        )
    unfreeze_wallets.short_description = "Unfreeze selected wallets"
    
    def mark_kyc_verified(self, request, queryset):
        """Mark selected wallets as KYC verified"""
        updated = queryset.update(is_kyc_verified=True)
        self.message_user(
            request, 
            f'{updated} wallet(s) were marked as KYC verified.'
        )
    mark_kyc_verified.short_description = "Mark as KYC verified"

