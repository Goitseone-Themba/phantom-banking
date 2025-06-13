from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MerchantViewSet

router = DefaultRouter()
router.register(r'', MerchantViewSet, basename='merchants')

app_name = 'merchants'

urlpatterns = [
    path('', include(router.urls)),
]
