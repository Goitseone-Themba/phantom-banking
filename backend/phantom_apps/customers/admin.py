from django.contrib import admin
from django.utils import timezone
from .models import Customer, MerchantCustomerAccess

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'wallet_created_by', 'status', 'created_at']
    list_filter = ['status', 'is_verified', 'created_at', 'wallet_created_by']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email', 'identity_number']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'customer_id',
                'first_name',
                'last_name',
                'phone_number',
                'email',
                'identity_number',
            )
        }),
        ('Status & Verification', {
            'fields': (
                'status',
                'is_verified',
            )
        }),
        ('Preferences', {
            'fields': (
                'preferred_language',
                'nationality',
            )
        }),
        ('Wallet Creation', {
            'fields': (
                'wallet_created_by',
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


@admin.register(MerchantCustomerAccess)
class MerchantCustomerAccessAdmin(admin.ModelAdmin):
    """Admin-only interface for managing merchant access to customer wallets"""
    
    list_display = [
        'merchant', 'customer', 'access_type', 'grant_reason', 
        'is_active', 'granted_at', 'expires_at'
    ]
    list_filter = [
        'access_type', 'grant_reason', 'is_active', 
        'granted_at', 'expires_at', 'last_modified_at'
    ]
    search_fields = [
        'merchant__business_name',
        'customer__first_name',
        'customer__last_name',
        'customer__phone_number'
    ]
    readonly_fields = [
        'granted_at', 'last_modified_at', 'created_by_merchant'
    ]
    
    fieldsets = (
        ('⚠️ ADMIN ONLY - Access Control', {
            'fields': (
                'merchant',
                'customer',
                'access_type',
                'grant_reason',
                'is_active',
                'expires_at',
            ),
            'description': 'Only administrators can modify merchant access to customer wallets.'
        }),
        ('Access History', {
            'fields': (
                'granted_at',
                'created_by_merchant',
                'last_modified_at',
            ),
            'classes': ('collapse',)
        }),
        ('Suspension Management', {
            'fields': (
                'suspension_reason',
            ),
            'classes': ('collapse',),
            'description': 'Use when suspending merchant access'
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'merchant', 'customer', 'created_by_merchant'
        )
    
    def save_model(self, request, obj, form, change):
        """Track admin who modifies access"""
        # For now, we'll track changes in suspension_reason field
        if change:
            if obj.suspension_reason and not obj.suspension_reason.endswith(f"[Modified by {request.user.username}]"):
                obj.suspension_reason += f" [Modified by {request.user.username}]"
        super().save_model(request, obj, form, change)
    
    actions = ['suspend_access', 'reactivate_access', 'extend_access']
    
    def suspend_access(self, request, queryset):
        """Suspend merchant access to wallets"""
        updated = queryset.update(
            access_type='suspended',
            is_active=False,
            suspension_reason=f"Suspended by admin {request.user.username} on {timezone.now()}"
        )
        self.message_user(request, f'{updated} access permissions suspended.')
    suspend_access.short_description = "🚫 Suspend selected access permissions"
    
    def reactivate_access(self, request, queryset):
        """Reactivate suspended merchant access"""
        updated = queryset.filter(access_type='suspended').update(
            access_type='full',
            is_active=True,
            suspension_reason=f"Reactivated by admin {request.user.username} on {timezone.now()}"
        )
        self.message_user(request, f'{updated} access permissions reactivated.')
    reactivate_access.short_description = "✅ Reactivate suspended access permissions"
    
    def extend_access(self, request, queryset):
        """Extend access expiration by 1 year"""
        from datetime import timedelta
        new_expiry = timezone.now() + timedelta(days=365)
        updated = queryset.update(
            expires_at=new_expiry
        )
        self.message_user(request, f'{updated} access permissions extended to {new_expiry.date()}.')
    extend_access.short_description = "📅 Extend access by 1 year"
