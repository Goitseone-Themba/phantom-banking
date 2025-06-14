from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    EmailVerificationToken,
    PasswordResetToken,
    LoginAttempt,
    UserSession
)

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Extended User admin with additional fields"""
    
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'user_type', 'is_email_verified', 'is_active',
        'date_joined', 'last_login'
    ]
    list_filter = [
        'user_type', 'is_active', 'is_email_verified',
        'is_phone_verified', 'is_business_verified',
        'date_joined', 'last_login'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'business_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': (
                'phone_number', 'date_of_birth', 'user_type',
                'business_name', 'business_registration'
            )
        }),
        ('Verification Status', {
            'fields': (
                'is_email_verified', 'email_verified_at',
                'is_phone_verified', 'phone_verified_at',
                'is_business_verified'
            )
        }),
        ('Security', {
            'fields': (
                'failed_login_attempts', 'account_locked_until',
                'last_login_ip'
            )
        }),
        ('Terms and Privacy', {
            'fields': (
                'terms_accepted_at', 'privacy_accepted_at'
            )
        }),
    )
    
    readonly_fields = [
        'email_verified_at', 'phone_verified_at',
        'failed_login_attempts', 'last_login_ip',
        'terms_accepted_at', 'privacy_accepted_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Email verification token admin"""
    
    list_display = [
        'user', 'email', 'created_at', 'expires_at',
        'is_expired', 'is_used', 'used_at'
    ]
    list_filter = ['created_at', 'expires_at', 'used_at']
    search_fields = ['user__email', 'email', 'token']
    readonly_fields = ['token', 'created_at', 'expires_at', 'used_at']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def is_used(self, obj):
        return obj.is_used
    is_used.boolean = True
    is_used.short_description = 'Used'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Password reset token admin"""
    
    list_display = [
        'user', 'created_at', 'expires_at', 'ip_address',
        'is_expired', 'is_used', 'used_at'
    ]
    list_filter = ['created_at', 'expires_at', 'used_at']
    search_fields = ['user__email', 'token', 'ip_address']
    readonly_fields = ['token', 'created_at', 'expires_at', 'used_at']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def is_used(self, obj):
        return obj.is_used
    is_used.boolean = True
    is_used.short_description = 'Used'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Login attempt admin"""
    
    list_display = [
        'email_attempted', 'user', 'success', 'failure_reason',
        'ip_address', 'attempted_at', 'country', 'city'
    ]
    list_filter = [
        'success', 'failure_reason', 'attempted_at',
        'country', 'city'
    ]
    search_fields = [
        'email_attempted', 'user__email', 'ip_address',
        'user_agent', 'country', 'city'
    ]
    readonly_fields = ['attempted_at']
    ordering = ['-attempted_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False  # These should only be created automatically


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """User session admin"""
    
    list_display = [
        'user', 'ip_address', 'device_type', 'browser',
        'os', 'is_active', 'created_at', 'last_activity'
    ]
    list_filter = [
        'is_active', 'device_type', 'browser', 'os',
        'created_at', 'last_activity'
    ]
    search_fields = [
        'user__email', 'ip_address', 'session_key',
        'user_agent', 'device_type', 'browser', 'os'
    ]
    readonly_fields = ['session_key', 'created_at', 'last_activity']
    ordering = ['-last_activity']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['deactivate_sessions']
    
    def deactivate_sessions(self, request, queryset):
        """Deactivate selected sessions"""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Successfully deactivated {count} session(s).'
        )
    deactivate_sessions.short_description = 'Deactivate selected sessions'


# Customize admin site header
admin.site.site_header = 'Phantom Banking Administration'
admin.site.site_title = 'Phantom Banking Admin'
admin.site.index_title = 'Welcome to Phantom Banking Administration'

