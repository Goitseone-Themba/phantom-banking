from django.urls import path, include
from . import views

app_name = 'transactions'

urlpatterns = [
    # QR Code Payment APIs
    path('qr/create/', views.QRCodeCreateView.as_view(), name='qr-create'),
    path('qr/<str:qr_token>/', views.QRCodeDetailView.as_view(), name='qr-detail'),
    path('qr/<str:qr_token>/pay/', views.process_qr_payment, name='qr-payment'),
    path('qr/<str:qr_token>/image/', views.get_qr_image, name='qr-image'),
    
    # EFT Payment APIs
    path('eft/initiate/', views.EFTPaymentCreateView.as_view(), name='eft-initiate'),
    path('eft/<uuid:id>/status/', views.EFTPaymentStatusView.as_view(), name='eft-status'),
    path('eft/webhook/', views.eft_webhook_handler, name='eft-webhook'),
    
    # Transaction APIs
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
]