from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('security.urls')),
    path('api/kyc/', include('phantom_apps.kyc.urls')),
    path('api/wallets/', include('phantom_apps.wallets.urls')),
    path('api/payments/', include('phantom_apps.payments.urls')),
    path('api/transactions/', include('phantom_apps.transactions.urls')),
    path('api/merchants/', include('phantom_apps.merchants.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)