from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KYCRecordViewSet, VeriffWebhookView, kyc_summary

router = DefaultRouter()
router.register(r'records', KYCRecordViewSet, basename='kyc-records')

urlpatterns = [
    path('api/kyc/', include(router.urls)),
    path('api/kyc/webhook/veriff/', VeriffWebhookView.as_view(), name='veriff-webhook'),
    path('api/kyc/summary/', kyc_summary, name='kyc-summary'),
]