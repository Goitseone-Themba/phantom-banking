from django.contrib import admin
from .models import Transaction, QRCode, EFTPayment, PaymentMethod, TransactionStatus


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(TransactionStatus)
class TransactionStatusAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['qr_token', 'merchant', 'amount', 'status', 'expires_at', 'created_at']
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = ['qr_token', 'merchant__business_name', 'description']
    readonly_fields = ['qr_token', 'qr_data', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('merchant', 'amount', 'description', 'reference')
        }),
        ('QR Code Details', {
            'fields': ('qr_token', 'qr_data', 'status', 'expires_at')
        }),
        ('Payment Tracking', {
            'fields': ('customer', 'transaction')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EFTPayment)
class EFTPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'amount', 'bank_code', 'status', 'created_at']
    list_filter = ['status', 'bank_code', 'created_at']
    search_fields = ['customer__full_name', 'reference', 'external_reference']
    readonly_fields = ['id', 'created_at', 'processed_at', 'completed_at', 'response_data']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'wallet')
        }),
        ('Payment Details', {
            'fields': ('amount', 'bank_code', 'account_number', 'reference')
        }),
        ('Processing Information', {
            'fields': ('status', 'external_reference', 'response_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Related Records', {
            'fields': ('transaction',)
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'customer', 'merchant', 'transaction_type', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at', 'payment_method']
    search_fields = ['transaction_id', 'customer__full_name', 'merchant__business_name', 'reference', 'reference_number']
    readonly_fields = ['transaction_id', 'net_amount', 'reference_number', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('transaction_type', 'amount', 'fee', 'net_amount', 'currency')
        }),
        ('Parties Involved', {
            'fields': ('customer', 'merchant', 'wallet', 'from_wallet', 'to_wallet')
        }),
        ('Status and Method', {
            'fields': ('status', 'payment_method')
        }),
        ('References', {
            'fields': ('reference', 'reference_number', 'external_reference', 'description')
        }),
        ('Additional Data', {
            'fields': ('metadata', 'payment_details'),
            'classes': ('collapse',)
        }),
        ('Reconciliation', {
            'fields': ('is_reconciled', 'failure_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'merchant', 'status', 'payment_method'
        )