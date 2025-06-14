from django.urls import path
from . import views

app_name = 'wallets'

urlpatterns = [
    # Wallets API root endpoint
    path('', views.wallets_api_root, name='wallets_api_root'),
    
    # Relationship-centric wallet creation
    path(
        'merchants/me/customers/<uuid:customer_id>/wallet/',
        views.create_customer_wallet,
        name='create_customer_wallet'
    ),
    
    # Customer wallet access
    path(
        'customers/<uuid:customer_id>/wallet/',
        views.get_customer_wallet,
        name='get_customer_wallet'
    ),
    
    # Merchant wallets listing
    path(
        'merchants/<uuid:merchant_id>/wallets/',
        views.list_merchant_wallets,
        name='list_merchant_wallets'
    ),
    
    # Merchant data integrity check
    path(
        'merchants/<uuid:merchant_id>/integrity/',
        views.verify_data_integrity,
        name='verify_merchant_data_integrity'
    ),
]
