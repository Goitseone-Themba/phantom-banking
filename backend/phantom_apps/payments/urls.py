from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'providers', views.PaymentProviderViewSet, basename='payment-provider')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'refunds', views.PaymentRefundViewSet, basename='payment-refund')

urlpatterns = [
    path('', include(router.urls)),
]