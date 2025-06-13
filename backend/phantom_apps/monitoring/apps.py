from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.monitoring'
    verbose_name = 'Monitoring & Metrics'
    
    def ready(self):
        """Initialize monitoring when Django starts"""
        from . import metrics  # Import to register metrics
        from . import signals  # Import to register signal handlers

