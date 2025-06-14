from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.authentication'
    verbose_name = 'Authentication'

    def ready(self):
        # Import signal handlers when the app is ready
        try:
            import phantom_apps.authentication.signals  # noqa
        except ImportError:
            pass

