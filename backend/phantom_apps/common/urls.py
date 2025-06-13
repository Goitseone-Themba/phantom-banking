from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('health/database/', views.DatabaseHealthView.as_view(), name='database_health'),
]
