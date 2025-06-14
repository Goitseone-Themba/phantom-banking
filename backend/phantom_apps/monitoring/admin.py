from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html


class MonitoringAdminSite(admin.AdminSite):
    """Custom admin site with monitoring dashboard"""
    site_header = 'Phantom Banking Admin'
    site_title = 'Phantom Banking Admin'
    index_title = 'Phantom Banking Administration'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('monitoring/dashboard/', self.admin_view(self.monitoring_dashboard), name='monitoring_dashboard'),
        ]
        return custom_urls + urls
    
    def monitoring_dashboard(self, request):
        """Redirect to monitoring dashboard"""
        from .views import AdminDashboardView
        return AdminDashboardView.as_view()(request)
    
    def index(self, request, extra_context=None):
        """Custom admin index with monitoring links"""
        extra_context = extra_context or {}
        extra_context['monitoring_links'] = [
            {
                'title': 'System Dashboard',
                'url': reverse('admin:monitoring_dashboard'),
                'description': 'View system performance metrics and health status'
            },
            {
                'title': 'Prometheus Metrics',
                'url': reverse('monitoring:metrics'),
                'description': 'Raw Prometheus metrics endpoint'
            },
            {
                'title': 'Health Check',
                'url': reverse('monitoring:health'),
                'description': 'System health status'
            },
        ]
        return super().index(request, extra_context)


# Create custom admin site instance
monitoring_admin_site = MonitoringAdminSite(name='monitoring_admin')

