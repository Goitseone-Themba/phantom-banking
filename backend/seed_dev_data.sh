#!/bin/bash

# Development Data Seeding Script for Phantom Banking
# This script populates the database with comprehensive dummy data for development

echo "🚀 Phantom Banking - Development Data Seeding"
echo "==============================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Virtual environment not detected. Activating..."
    source .venv/bin/activate || {
        echo "❌ Failed to activate virtual environment. Please run 'source .venv/bin/activate' first."
        exit 1
    }
fi

# Parse command line arguments
CLEAR=""
MERCHANTS=8
CUSTOMERS=15
TRANSACTIONS=10

while [[ $# -gt 0 ]]; do
    case $1 in
        --clear)
            CLEAR="--clear"
            echo "🗑️  Will clear existing data before seeding"
            shift
            ;;
        --merchants)
            MERCHANTS="$2"
            shift 2
            ;;
        --customers)
            CUSTOMERS="$2"
            shift 2
            ;;
        --transactions)
            TRANSACTIONS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --clear                    Clear existing data before seeding"
            echo "  --merchants NUM           Number of merchants to create (default: 8)"
            echo "  --customers NUM           Average customers per merchant (default: 15)"
            echo "  --transactions NUM        Average transactions per customer (default: 10)"
            echo "  --help                    Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                        # Seed with default values"
            echo "  $0 --clear               # Clear existing data and seed"
            echo "  $0 --merchants 5 --customers 20  # Custom merchant and customer counts"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "📊 Configuration:"
echo "   Merchants: $MERCHANTS"
echo "   Customers per merchant: ~$CUSTOMERS"
echo "   Transactions per customer: ~$TRANSACTIONS"
echo ""

# Confirm if clearing data
if [[ "$CLEAR" == "--clear" ]]; then
    echo "⚠️  This will DELETE ALL existing data!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled by user"
        exit 1
    fi
fi

# Run database migrations first
echo "🔄 Running database migrations..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ Database migration failed. Please check your database configuration."
    exit 1
fi

# Run the seeding command
echo "🌱 Starting data seeding..."
python manage.py seed_dev_data \
    $CLEAR \
    --merchants $MERCHANTS \
    --customers-per-merchant $CUSTOMERS \
    --transactions-per-customer $TRANSACTIONS

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Data seeding completed successfully!"
    echo ""
    echo "🔑 Sample Login Credentials:"
    echo "   Merchants: merchant_1_retail_store, merchant_2_restaurant, etc."
    echo "   Password: dev_password_123"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Start the development server: python manage.py runserver"
    echo "   2. Visit the admin panel: http://localhost:8000/admin/"
    echo "   3. Check API docs: http://localhost:8000/api/docs/"
    echo "   4. Test API endpoints with the created merchant accounts"
    echo ""
    echo "📈 Database populated with:"
    echo "   - Multiple merchant types (retail, restaurant, pharmacy, etc.)"
    echo "   - Customers with varied verification statuses"
    echo "   - Wallets with realistic balances"
    echo "   - KYC records with different approval states"
    echo "   - Transaction history"
    echo "   - QR codes and EFT payments"
else
    echo "❌ Data seeding failed. Check the error messages above."
    exit 1
fi

