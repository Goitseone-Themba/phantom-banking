#!/bin/bash

echo "🏦 Creating Phantom Banking Complete Django Backend Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}


# Create core_apps directory
print_info "Creating phantom_apps directory..."
# mkdir -p apps
touch phantom_apps/__init__.py

# Create Django apps
APPS=("merchants" "wallets" "transactions" "customers" "kyc" "payments")
MOCK_APPS=("fnb" "mobile_money")

print_info "Creating Django apps..."

# Create main apps
for app in "${APPS[@]}"; do
    print_info "Creating app: $app"
    python manage.py startapp $app phantom_apps/$app
done

# Create mock systems
mkdir -p phantom_apps/mock_systems
touch phantom_apps/mock_systems/__init__.py

for mock_app in "${MOCK_APPS[@]}"; do
    print_info "Creating mock app: $mock_app"
    python manage.py startapp $mock_app phantom_apps/mock_systems/$mock_app
done

# Create common utilities
mkdir -p phantom_apps/common
touch phantom_apps/common/__init__.py

# Create payment providers directory
mkdir -p phantom_apps/payments/providers
touch phantom_apps/payments/providers/__init__.py

