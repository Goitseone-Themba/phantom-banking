#!/usr/bin/env python
"""
Script to run Django tests with debug toolbar disabled.
Usage: python run_django_tests.py [test_labels] [options]
Example: python run_django_tests.py tests.components.test_customer_association_api --keepdb
"""
import os
import sys
import django
from django.conf import settings

def main():
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Initialize Django
    django.setup()
    
    # Disable the debug toolbar by removing it from INSTALLED_APPS and MIDDLEWARE
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'debug_toolbar']
    
    if 'debug_toolbar.middleware.DebugToolbarMiddleware' in settings.MIDDLEWARE:
        settings.MIDDLEWARE = [m for m in settings.MIDDLEWARE if m != 'debug_toolbar.middleware.DebugToolbarMiddleware']
    
    # Run the tests
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'test'] + sys.argv[1:])

if __name__ == '__main__':
    main()
