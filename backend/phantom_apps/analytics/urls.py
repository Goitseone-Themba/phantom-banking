# phantom_apps/analytics/urls.py

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main analytics dashboard
    path('', views.analytics_dashboard, name='dashboard'),
    
    # Customer detail analytics
    path('customer/<str:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # API endpoints for chart data
    path('api/data/', views.analytics_api_data, name='api_data'),
    
    # Class-based view alternative
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='dashboard_cbv'),
]