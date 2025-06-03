from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/OpenAPI configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Phantom Banking API",
        default_version='v1',
        description="API documentation for Phantom Banking System",
        terms_of_service="https://www.phantom-banking.com/terms/",
        contact=openapi.Contact(email="contact@phantom-banking.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('security.urls')),  # Security endpoints
    
    # Swagger/OpenAPI documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]