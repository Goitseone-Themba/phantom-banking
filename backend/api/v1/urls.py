from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Core business endpoints
    path('merchants/', include('phantom_apps.merchants.urls')),
    path('customers/', include('phantom_apps.customers.urls')),
    path('wallets/', include('phantom_apps.wallets.urls')),
    path('transactions/', include('phantom_apps.transactions.urls')),
    
    # Mock systems
    path('mock-fnb/', include('phantom_apps.mock_systems.fnb.urls')),
    path('mock-mobile-money/', include('phantom_apps.mock_systems.mobile_money.urls')),
    
    # Common utilities
    path('', include('phantom_apps.common.urls')),
]
