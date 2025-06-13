from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'merchant', 'status', 'created_at']
    list_filter = ['status', 'is_verified', 'created_at', 'merchant']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']
