from django.apps import AppConfig

class KycConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.kyc'
    verbose_name = 'KYC Management'

    def ready(self):
        import phantom_apps.kyc.signals  # Import signals when app is ready