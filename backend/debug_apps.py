import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

print("=== DJANGO APP DETECTION DEBUG ===\n")

# 1. Check INSTALLED_APPS
from django.conf import settings
print("1. INSTALLED_APPS check:")
for app in settings.INSTALLED_APPS:
    if 'phantom' in app:
        print(f"   ✅ {app}")

# 2. Check Django can find apps
from django.apps import apps
print("\n2. Django registered apps:")
for app_config in apps.get_app_configs():
    if 'phantom' in app_config.label:
        print(f"   ✅ {app_config.label}: {app_config.name}")

# 3. Check model imports
print("\n3. Model import test:")
try:
    import phantom_apps.merchants.models
    print("   ✅ phantom_apps.merchants.models imported")
except Exception as e:
    print(f"   ❌ phantom_apps.merchants.models: {e}")

# 4. Check specific model classes
try:
    from phantom_apps.merchants.models import Merchant
    print("   ✅ Merchant class found")
    print(f"      Fields: {[f.name for f in Merchant._meta.fields]}")
except Exception as e:
    print(f"   ❌ Merchant class: {e}")

print("\n=== END DEBUG ===")