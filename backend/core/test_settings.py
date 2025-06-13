"""
Test settings for Phantom Banking project.
"""
from core.settings import *

# Disable Debug Toolbar during tests
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
    'IS_RUNNING_TESTS': True,
}

# Remove debug_toolbar from INSTALLED_APPS during tests
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# Remove debug_toolbar middleware during tests
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

# Disable migrations for tests to speed up test execution
# Commented out to allow for table creation
# MIGRATION_MODULES = {app.split('.')[-1]: 'phantom_apps.nomigrations' for app in INSTALLED_APPS}

# Keep the test database between test runs (similar effect to --no-migrations)
TEST_KEEPDB = True

# To use this configuration effectively:
# 1. First run without the MIGRATION_MODULES setting to create the tables
# 2. For subsequent runs, uncomment the MIGRATION_MODULES setting to skip migrations
# 3. Always use --keepdb flag to reuse the test database

