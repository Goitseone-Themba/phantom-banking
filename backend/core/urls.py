from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

def health_check(request):
    """Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy', 
        'service': 'phantom-banking',
        'version': '1.0.0',
        'django_version': '5.2+',
        'api_version': 'v1'
    })

def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        'api': 'Phantom Banking API',
        'version': '1.0.0',
        'description': 'Embedded Accounts for the Unbanked - FNB Hackathon 2025',
        'documentation': '/api/docs/',
        'health_check': '/health/',
        'admin': '/admin/',
        'endpoints': {
            'authentication': '/api/v1/auth/',
            'merchants': '/api/v1/merchants/',
            'customers': '/api/v1/customers/',
            'wallets': '/api/v1/wallets/',
            'transactions': '/api/v1/transactions/',
            'health': '/api/v1/health/',
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health checks and info (top level)
    path('health/', health_check, name='health_check'),
    path('', api_info, name='api_info'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # JWT Authentication endpoints
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Authentication (with trailing slash)
    path('api/v1/auth/', include('phantom_apps.authentication.urls')),
    
    # API v1 endpoints
    path('api/v1/', include('api.v1.urls')),
    
    
    # Direct app access (for development/debugging)
    path('dev/kyc/', include('phantom_apps.kyc.urls')),
    path('dev/common/', include('phantom_apps.common.urls')),
    path('dev/merchants/', include('phantom_apps.merchants.urls')),
    path('dev/customers/', include('phantom_apps.customers.urls')),
    path('dev/wallets/', include('phantom_apps.wallets.urls')),
    path('dev/transactions/', include('phantom_apps.transactions.urls')),
    path('dev/monitoring/', include('phantom_apps.monitoring.urls')),
    
    # Mock systems
    path('mock/fnb/', include('phantom_apps.mock_systems.fnb.urls')),
    path('mock/mobile-money/', include('phantom_apps.mock_systems.mobile_money.urls')),
]

# Development-specific URLs
if settings.DEBUG:
    # Static and media files for development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar 
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        urlpatterns = [
            path('__debug__/', include('debug_toolbar.urls')),
        ] + urlpatterns

# Admin customization for Phantom Banking
admin.site.site_header = "Phantom Banking Admin"
admin.site.site_title = "Phantom Banking"
admin.site.index_title = "Welcome to Phantom Banking Administration"
admin.site.site_url = "/api/docs/"  # Link to API docs from admin
