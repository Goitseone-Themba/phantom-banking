from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('metrics/', views.metrics_view, name='metrics'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),
    path('api/dashboard-data/', views.DashboardDataView.as_view(), name='dashboard_data'),
]

