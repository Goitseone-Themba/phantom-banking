from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, WalletCreationRequestViewSet

router = DefaultRouter()
router.register(r'wallets', WalletViewSet)
router.register(r'wallet-creation', WalletCreationRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]