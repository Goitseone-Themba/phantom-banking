#!/bin/bash

# Script to run a specific Django test case
# Usage: ./run_test_case.sh module.TestClass.test_method

if [ -z "$1" ]; then
    echo "Error: You must specify a test case to run."
    echo "Usage: ./run_test_case.sh module.TestClass.test_method"
    echo "Example: ./run_test_case.sh tests.components.test_wallet_creation_api.WalletCreationAPITest.test_customer_not_found"
    exit 1
fi

# Make sure the database is created
if [ ! -f .test_db_created ]; then
    echo "First run - creating test database with tables..."
    DJANGO_SETTINGS_MODULE=core.test_settings python manage.py test --keepdb --verbosity 0
    touch .test_db_created
    echo "Test database created successfully."
fi

# Run the specific test case
echo "Running test case: $1"
DJANGO_SETTINGS_MODULE=core.test_settings python manage.py test "$1" --keepdb

