from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'merchants', views.MerchantViewSet, basename='merchant')
router.register(r'merchant-accounts', views.MerchantAccountViewSet, basename='merchant-account')
router.register(r'merchant-transactions', views.MerchantTransactionViewSet, basename='merchant-transaction')

urlpatterns = [
    path('', include(router.urls)),
]