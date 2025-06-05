from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import QRCode, EFTPayment, Transaction


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = [
        'qr_token', 'merchant', 'amount', 'status', 
        'is_valid', 'expires_at', 'created_at'
    ]
    list_filter = ['status', 'merchant', 'created_at', 'expires_at']
    search_fields = ['qr_token', 'description', 'reference', 'merchant__business_name']
    readonly_fields = ['id', 'qr_token', 'qr_data', 'created_at', 'updated_at']
    
    fieldsets = (
        ('QR Code Information', {
            'fields': ('id', 'qr_token', 'merchant', 'amount', 'description', 'reference')
        }),
        ('Status & Timing', {
            'fields': ('status', 'expires_at', 'created_at', 'updated_at')
        }),
        ('Payment Details', {
            'fields': ('customer', 'transaction')
        }),
        ('QR Data', {
            'fields': ('qr_data',),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Valid'


@admin.register(EFTPayment)
class EFTPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'amount', 'bank_code', 
        'status', 'external_reference', 'created_at'
    ]
    list_filter = ['status', 'bank_code', 'created_at', 'processed_at']
    search_fields = [
        'customer__phone_number', 'customer__full_name',
        'account_number', 'reference', 'external_reference'
    ]
    readonly_fields = [
        'id', 'external_reference', 'response_data',
        'created_at', 'processed_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('customer', 'wallet', 'amount', 'reference')
        }),
        ('Bank Details', {
            'fields': ('bank_code', 'account_number')
        }),
        ('Status & Processing', {
            'fields': ('status', 'external_reference', 'created_at', 'processed_at', 'completed_at')
        }),
        ('Transaction Link', {
            'fields': ('transaction',)
        }),
        ('Response Data', {
            'fields': ('response_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['completed', 'failed', 'cancelled']:
            return self.readonly_fields + ['customer', 'wallet', 'amount', 'bank_code', 'account_number']
        return self.readonly_fields


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'transaction_type', 'customer', 'merchant',
        'amount', 'fee', 'status', 'created_at'
    ]
    list_filter = [
        'transaction_type', 'status', 'created_at',
        'merchant', 'completed_at'
    ]
    search_fields = [
        'customer__phone_number', 'customer__full_name',
        'merchant__business_name', 'reference', 'description'
    ]
    readonly_fields = [
        'id', 'net_amount', 'created_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('id', 'transaction_type', 'amount', 'fee', 'net_amount')
        }),
        ('Parties', {
            'fields': ('customer', 'merchant')
        }),
        ('Wallets', {
            'fields': ('from_wallet', 'to_wallet')
        }),
        ('Status & Details', {
            'fields': ('status', 'reference', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['completed', 'failed', 'cancelled']:
            return self.readonly_fields + [
                'transaction_type', 'amount', 'fee', 'customer',
                'merchant', 'from_wallet', 'to_wallet'
            ]
        return self.readonly_fields


# Register related models for easy access
from phantom_apps.customers.models import Customer
from phantom_apps.merchants.models import Merchant
from phantom_apps.wallets.models import Wallet

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'full_name', 'email', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified', 'created_at']
    search_fields = ['phone_number', 'full_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'business_type', 'contact_email', 'is_active', 'is_verified', 'created_at']
    list_filter = ['business_type', 'is_active', 'is_verified', 'created_at']
    search_fields = ['business_name', 'contact_email', 'business_registration']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['customer', 'merchant', 'formatted_balance', 'wallet_type', 'is_active', 'created_at']
    list_filter = ['wallet_type', 'is_active', 'is_frozen', 'merchant', 'created_at']
    search_fields = ['customer__phone_number', 'customer__full_name', 'merchant__business_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_transaction_at']
    
    def formatted_balance(self, obj):
        return obj.formatted_balance
    formatted_balance.short_description = 'Balance'