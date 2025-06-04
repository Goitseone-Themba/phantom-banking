from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'verifications', views.KYCVerificationViewSet, basename='kyc-verification')
router.register(r'fnb-conversions', views.FNBAccountConversionViewSet, basename='fnb-conversion')

urlpatterns = [
    path('', include(router.urls)),
]