from django.apps import AppConfig

class TransactionsConfig(AppConfig):
    """Configuration for the Transactions app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.transactions'
    verbose_name = 'Transactions'

def ready(self):
        # Import signal handlers when app is ready
        try:
            import phantom_apps.transactions.signals
        except ImportError:
            pass