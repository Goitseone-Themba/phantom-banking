from django.contrib import admin
from .models import Merchant, APICredential

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'contact_email', 'phone_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['business_name', 'contact_email', 'business_registration']
    readonly_fields = ['merchant_id', 'created_at', 'updated_at']

@admin.register(APICredential)
class APICredentialAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'api_key', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['credential_id', 'created_at']
