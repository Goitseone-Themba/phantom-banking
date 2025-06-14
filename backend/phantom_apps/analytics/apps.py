# phantom_apps/analytics/apps.py

from django.apps import AppConfig

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.analytics'
    verbose_name = 'Financial Analytics'
    
    def ready(self):
        """Initialize app when Django starts"""
        pass