#!/usr/bin/env python
import os
import sys
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import Django settings after setting the environment variable
django.setup()

# Import settings and modify the debug toolbar configuration
from django.conf import settings
if hasattr(settings, 'DEBUG_TOOLBAR_CONFIG'):
    settings.DEBUG_TOOLBAR_CONFIG['IS_RUNNING_TESTS'] = False

# Run the tests
from django.core.management import execute_from_command_line
execute_from_command_line([sys.argv[0], 'test'] + sys.argv[1:])
