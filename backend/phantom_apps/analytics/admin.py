# phantom_apps/analytics/admin.py

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.html import format_html

class AnalyticsAdminConfig(admin.AdminConfig):
    """Custom admin configuration for analytics"""
    default_site = 'phantom_apps.analytics.admin.AnalyticsAdminSite'

class AnalyticsAdminSite(admin.AdminSite):
    """Custom admin site with analytics integration"""
    
    site_header = "Phantom Banking Analytics"
    site_title = "Analytics Admin"
    index_title = "Financial Analytics Dashboard"
    
    def get_urls(self):
        """Add custom analytics URLs to admin"""
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.analytics_dashboard, name='analytics_dashboard'),
            path('analytics/customer/<str:customer_id>/', self.customer_detail, name='analytics_customer_detail'),
        ]
        return custom_urls + urls
    
    def analytics_dashboard(self, request):
        """Redirect to analytics dashboard"""
        from .views import analytics_dashboard
        return analytics_dashboard(request)
    
    def customer_detail(self, request, customer_id):
        """Redirect to customer detail"""
        from .views import customer_detail
        return customer_detail(request, customer_id)
    
    def index(self, request, extra_context=None):
        """Custom admin index with analytics links"""
        extra_context = extra_context or {}
        
        # Add analytics quick links
        extra_context.update({
            'analytics_enabled': True,
            'analytics_url': reverse('admin:analytics_dashboard'),
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
analytics_admin_site = AnalyticsAdminSite(name='analytics_admin')

# Mock admin models for demonstration
class MockAnalyticsAdmin:
    """Mock admin class for analytics display"""
    
    def __init__(self):
        self.verbose_name = "Financial Analytics"
        self.verbose_name_plural = "Financial Analytics"
    
    def has_module_perms(self, request):
        return request.user.is_staff
    
    def get_urls(self):
        return []

# Register mock analytics in regular admin
@admin.register
class AnalyticsProxy(admin.ModelAdmin):
    """Proxy admin for analytics in main admin interface"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist to redirect to analytics dashboard"""
        return redirect('analytics:dashboard')

# Custom admin actions
def export_analytics_data(modeladmin, request, queryset):
    """Export analytics data as JSON"""
    from .models import AnalyticsDataManager
    import json
    from django.http import JsonResponse
    
    data = {
        'customers': len(AnalyticsDataManager.get_customers()),
        'transactions': len(AnalyticsDataManager.get_transactions()),
        'merchants': len(AnalyticsDataManager.get_merchants()),
        'export_date': str(datetime.now())
    }
    
    return JsonResponse(data)

export_analytics_data.short_description = "Export analytics summary"

# Admin site customizations
admin.site.site_header = "Phantom Banking Admin"
admin.site.site_title = "Phantom Banking"
admin.site.index_title = "Welcome to Phantom Banking Administration"

# Add analytics section to admin index
def get_admin_analytics_context():
    """Get analytics data for admin index page"""
    from .models import AnalyticsDataManager
    
    customers = AnalyticsDataManager.get_customers()
    transactions = AnalyticsDataManager.get_transactions()
    
    return {
        'analytics_summary': {
            'total_customers': len(customers),
            'total_transactions': len(transactions),
            'total_revenue': sum([t.amount for t in transactions]),
        }
    }