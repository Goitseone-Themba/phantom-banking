from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import MerchantUser, CustomerUser, AdminUser

User = get_user_model()

class BaseUserAdmin(UserAdmin):
    list_display = ('username', 'get_email', 'get_role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    def get_email(self, obj):
        return obj.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'email'
    
    def get_role(self, obj):
        return obj.role
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'role'
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'profile_image', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

admin.site.register(User, BaseUserAdmin)

@admin.register(MerchantUser)
class MerchantUserAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'registration_number', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('business_name', 'registration_number', 'user__username')

@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'national_id', 'phone_number')
    search_fields = ('first_name', 'last_name', 'national_id', 'user__username')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Name'

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'employee_id', 'access_level')
    search_fields = ('user__username', 'employee_id')