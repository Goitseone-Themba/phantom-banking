from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Merchant-authenticated views
    process_qr_payment_merchant,
    process_eft_payment_merchant,
    MerchantTransactionViewSet,
    
    # Public QR Code views
    QRCodeCreateView,
    QRCodeDetailView,
    process_qr_payment_public,
    get_qr_image,
    
    # Public EFT Payment views
    EFTPaymentCreateView,
    EFTPaymentStatusView,
    eft_webhook_handler,
    
    # Transaction listing and analytics
    TransactionListView,
    payment_analytics,
)

app_name = 'transactions'

# Router for ViewSets
router = DefaultRouter()
router.register(r'merchant/transactions', MerchantTransactionViewSet, basename='merchant-transactions')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # =============================================================================
    # Merchant-Authenticated Transaction Endpoints
    # =============================================================================
    
    # Merchant QR and EFT payment processing (requires authentication)
    path('merchant/qr-payment/', process_qr_payment_merchant, name='merchant-qr-payment'),
    path('merchant/eft-payment/', process_eft_payment_merchant, name='merchant-eft-payment'),
    
    # =============================================================================
    # Public QR Code Endpoints
    # =============================================================================
    
    # QR Code management (public endpoints)
    path('qr/create/', QRCodeCreateView.as_view(), name='qr-create'),
    path('qr/<str:qr_token>/', QRCodeDetailView.as_view(), name='qr-detail'),
    path('qr/<str:qr_token>/pay/', process_qr_payment_public, name='qr-payment'),
    path('qr/<str:qr_token>/image/', get_qr_image, name='qr-image'),
    
    # =============================================================================
    # Public EFT Payment Endpoints
    # =============================================================================
    
    # EFT Payment management (public endpoints)
    path('eft/initiate/', EFTPaymentCreateView.as_view(), name='eft-initiate'),
    path('eft/<uuid:id>/status/', EFTPaymentStatusView.as_view(), name='eft-status'),
    path('eft/webhook/', eft_webhook_handler, name='eft-webhook'),
    
    # =============================================================================
    # Transaction Listing and Analytics
    # =============================================================================
    
    # Transaction listing (public with filtering)
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    
    # Analytics endpoints
    path('analytics/', payment_analytics, name='payment-analytics'),
    
    # =============================================================================
    # Legacy/Compatibility Endpoints (optional)
    # =============================================================================
    
    # Alternative URL patterns for backward compatibility
    path('payments/qr/create/', QRCodeCreateView.as_view(), name='payments-qr-create'),
    path('payments/qr/<str:qr_token>/', QRCodeDetailView.as_view(), name='payments-qr-detail'),
    path('payments/qr/<str:qr_token>/pay/', process_qr_payment_public, name='payments-qr-payment'),
    path('payments/qr/<str:qr_token>/image/', get_qr_image, name='payments-qr-image'),
    
    path('payments/eft/initiate/', EFTPaymentCreateView.as_view(), name='payments-eft-initiate'),
    path('payments/eft/<uuid:id>/status/', EFTPaymentStatusView.as_view(), name='payments-eft-status'),
    path('payments/eft/webhook/', eft_webhook_handler, name='payments-eft-webhook'),
    
    path('payments/transactions/', TransactionListView.as_view(), name='payments-transaction-list'),
    path('payments/analytics/', payment_analytics, name='payments-analytics'),
]

# URL patterns for different API versions
v1_patterns = [
    # Version 1 API patterns (current)
    path('v1/transactions/', include(urlpatterns)),
]

# Alternative URL structure for different use cases
api_patterns = [
    # Direct API access
    path('api/transactions/', include(urlpatterns)),
    path('api/payments/', include([
        # QR Code endpoints
        path('qr/create/', QRCodeCreateView.as_view(), name='api-qr-create'),
        path('qr/<str:qr_token>/', QRCodeDetailView.as_view(), name='api-qr-detail'),
        path('qr/<str:qr_token>/pay/', process_qr_payment_public, name='api-qr-payment'),
        path('qr/<str:qr_token>/image/', get_qr_image, name='api-qr-image'),
        
        # EFT endpoints
        path('eft/initiate/', EFTPaymentCreateView.as_view(), name='api-eft-initiate'),
        path('eft/<uuid:id>/status/', EFTPaymentStatusView.as_view(), name='api-eft-status'),
        path('eft/webhook/', eft_webhook_handler, name='api-eft-webhook'),
        
        # Transaction endpoints
        path('transactions/', TransactionListView.as_view(), name='api-transaction-list'),
        path('analytics/', payment_analytics, name='api-analytics'),
    ])),
]

# URL patterns for mobile app
mobile_patterns = [
    path('mobile/v1/', include([
        # Mobile-optimized endpoints
        path('qr/create/', QRCodeCreateView.as_view(), name='mobile-qr-create'),
        path('qr/<str:qr_token>/pay/', process_qr_payment_public, name='mobile-qr-payment'),
        path('eft/topup/', EFTPaymentCreateView.as_view(), name='mobile-eft-topup'),
        path('transactions/', TransactionListView.as_view(), name='mobile-transactions'),
    ])),
]

# Webhook-specific patterns (for external bank integrations)
webhook_patterns = [
    path('webhooks/', include([
        # Bank webhook endpoints
        path('eft/', eft_webhook_handler, name='webhook-eft'),
        path('eft/fnb/', eft_webhook_handler, name='webhook-eft-fnb'),
        path('eft/standard/', eft_webhook_handler, name='webhook-eft-standard'),
        path('eft/barclays/', eft_webhook_handler, name='webhook-eft-barclays'),
        path('eft/nedbank/', eft_webhook_handler, name='webhook-eft-nedbank'),
        path('eft/choppies/', eft_webhook_handler, name='webhook-eft-choppies'),
    ])),
]

# Administrative patterns (for internal use)
admin_patterns = [
    path('admin/', include([
        # Administrative endpoints
        path('transactions/', MerchantTransactionViewSet.as_view({'get': 'list'}), name='admin-transactions'),
        path('analytics/', payment_analytics, name='admin-analytics'),
        
        # System health checks
        path('health/', payment_analytics, name='admin-health'),  # Reuse analytics for now
    ])),
]

# Export all patterns for flexible inclusion
__all__ = [
    'urlpatterns',
    'v1_patterns', 
    'api_patterns',
    'mobile_patterns',
    'webhook_patterns',
    'admin_patterns',
    'router'
]