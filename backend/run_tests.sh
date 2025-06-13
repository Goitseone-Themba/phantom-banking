#!/bin/bash

# Script to run Django tests with proper settings and flags
# Usage: ./run_tests.sh [test_module]

# Check if we need to create the database first
if [ ! -f .test_db_created ]; then
    echo "First run - creating test database with tables..."
    
    # First run: Create database tables
    DJANGO_SETTINGS_MODULE=core.test_settings python manage.py test --keepdb --verbosity 0
    
    # Mark database as created
    touch .test_db_created
    
    echo "Test database created successfully."
fi

# If a test module is specified, run just that test
if [ -n "$1" ]; then
    echo "Running test: $1"
    DJANGO_SETTINGS_MODULE=core.test_settings python manage.py test "$1" --keepdb
else
    echo "Running all tests..."
    DJANGO_SETTINGS_MODULE=core.test_settings python manage.py test --keepdb
fi

