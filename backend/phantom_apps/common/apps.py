from django.apps import AppConfig

class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.common'
    verbose_name = 'Common Utilities'
