from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_auth import MerchantRegistrationView

router = DefaultRouter()
router.register(r'merchants', views.MerchantViewSet, basename='merchant')
router.register(r'merchant-accounts', views.MerchantAccountViewSet, basename='merchant-account')
router.register(r'merchant-transactions', views.MerchantTransactionViewSet, basename='merchant-transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', MerchantRegistrationView.as_view(), name='merchant-register'),
    # Include security-related endpoints
    # Security and wallet endpoints are included at the project level
]