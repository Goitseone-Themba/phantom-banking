# Development Data Seeding Guide

This guide explains how to populate your Phantom Banking development database with comprehensive dummy data for testing and development purposes.

## Quick Start

```bash
# Simple seeding with default values
./seed_dev_data.sh

# Clear existing data and seed fresh
./seed_dev_data.sh --clear

# Custom configuration
./seed_dev_data.sh --merchants 10 --customers 20 --transactions 15
```

## What Gets Created

The seeding script creates realistic dummy data including:

### 🏪 **Merchants** (Default: 8)
- **Business Types**: Retail Store, Restaurant, Pharmacy, Gas Station, Supermarket, Electronics Store, Clothing Store, Hardware Store
- **Account Details**: User accounts, API credentials, business registration numbers
- **Status Mix**: 75% active, 25% inactive merchants
- **Realistic Data**: Phone numbers, emails, FNB account numbers, commission rates

### 👥 **Customers** (Default: ~15 per merchant)
- **Botswana Names**: Authentic first and last names (Thabo, Mpho, Keabetswe, etc.)
- **Contact Info**: Phone numbers (+267 format), emails (80% have email)
- **Verification Status**: Mix of verified and unverified customers
- **Geographic Data**: Botswana-focused with some regional diversity
- **Languages**: English and Setswana preferences

### 💰 **Wallets** (One per customer)
- **Balance Ranges**:
  - Basic wallets: P0 - P5,000
  - Verified wallets: P100 - P25,000
  - Premium wallets: P500 - P100,000
- **Limits**: Realistic daily/monthly limits based on wallet type
- **Status**: Active, inactive, or frozen based on customer status
- **KYC Integration**: Wallet type linked to verification status

### 🆔 **KYC Records** (One per customer)
- **Status Distribution**:
  - Verified customers: Mostly approved KYC
  - Unverified customers: Pending, in-progress, rejected, or resubmission requested
- **Complete Data**: Documents, events, risk scores, verification levels
- **Admin Integration**: KYC admin users for review processes
- **Realistic Timeline**: Verification dates, expiry dates, processing events

### 💳 **Transactions** (Default: ~10 per active customer)
- **Transaction Types**: QR payments, EFT top-ups, wallet transfers, merchant payments
- **Realistic Amounts**: Appropriate ranges for each transaction type
- **Status Distribution**: 80% completed, 20% pending/failed/cancelled
- **Historical Data**: Transactions spread over past 6 months
- **Metadata**: Device IDs, channels (mobile_app, web, api)

### 📱 **QR Codes** (3-10 per active merchant)
- **Status Mix**: Active, used, expired, cancelled
- **Realistic Expiry**: 15 minutes to 24 hours
- **Payment Integration**: Linked to merchants with proper amounts

### 🏦 **EFT Payments** (40% of customers have 1-5 payments)
- **Bank Integration**: FNB, Standard Bank, Barclays, Nedbank, Choppies
- **Status Variety**: Completed, pending, processing, failed
- **Realistic Processing**: Proper timing for different statuses

## Command Options

```bash
./seed_dev_data.sh [OPTIONS]

Options:
  --clear                    Clear existing data before seeding
  --merchants NUM           Number of merchants to create (default: 8)
  --customers NUM           Average customers per merchant (default: 15)
  --transactions NUM        Average transactions per customer (default: 10)
  --help                    Show help message
```

## Sample Accounts Created

### Merchant Accounts
- **Usernames**: `merchant_1_retail_store`, `merchant_2_restaurant`, etc.
- **Password**: `dev_password_123`
- **Email**: `merchant_X_type@phantombanking.dev`

### KYC Admin Accounts
- **Usernames**: `kyc_admin_1`, `kyc_admin_2`, `kyc_admin_3`
- **Role**: Staff users for KYC review processes

### Customer User Accounts
- **Usernames**: `customer_UUID`
- **Linked**: To KYC records for verification workflows

## Usage Examples

### Development Setup
```bash
# First time setup - clear any existing data
./seed_dev_data.sh --clear

# Start development server
python manage.py runserver
```

### Testing Different Scenarios
```bash
# Small dataset for quick testing
./seed_dev_data.sh --clear --merchants 3 --customers 5 --transactions 3

# Large dataset for load testing
./seed_dev_data.sh --clear --merchants 20 --customers 50 --transactions 25

# Add more data without clearing
./seed_dev_data.sh --merchants 5 --customers 10
```

### API Testing
```bash
# After seeding, you can test APIs with:
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "merchant_1_retail_store", "password": "dev_password_123"}'
```

## Data Relationships

```
Merchant 1:N Customer 1:1 Wallet
    |           |         |
API Creds   KYC Record   Transactions
    |           |         |
 Permissions  Documents  QR Codes
              Events    EFT Payments
```

## Verification Status Distribution

- **Verified Customers** (~66%): Approved KYC, verified/premium wallets, higher balances
- **Unverified Customers** (~33%): Various KYC statuses, basic wallets, lower limits
- **Active Merchants** (~75%): Full functionality, QR codes, transactions
- **Inactive Merchants** (~25%): Limited functionality for testing edge cases

## Geographic Distribution

- **Primary**: Botswana (BWA) - ~75% of customers
- **Regional**: South Africa (ZAF), Zimbabwe (ZWE), Namibia (NAM), Zambia (ZMB)
- **Cities**: Gaborone, Francistown, Molepolole, Selebi-Phikwe, Maun, Serowe, Kanye

## Database Performance

- **Default Dataset**: ~8 merchants, ~120 customers, ~1,200 transactions
- **Seeding Time**: 30-60 seconds depending on system
- **Database Size**: ~10-50MB depending on configuration
- **Indexes**: All properly indexed for performance testing

## Troubleshooting

### Common Issues

1. **Virtual Environment Not Activated**
   ```bash
   source .venv/bin/activate
   ./seed_dev_data.sh
   ```

2. **Database Migration Errors**
   ```bash
   python manage.py migrate
   ./seed_dev_data.sh
   ```

3. **Permission Denied**
   ```bash
   chmod +x seed_dev_data.sh
   ```

4. **Clear Data Safely**
   ```bash
   # The script will prompt for confirmation
   ./seed_dev_data.sh --clear
   ```

### Reset Everything
```bash
# Nuclear option - clear database and start fresh
python manage.py flush --noinput
python manage.py migrate
./seed_dev_data.sh
```

## Integration with Tests

The seeded data is perfect for:
- Manual API testing
- Frontend development
- Performance testing
- Integration testing
- Demo environments

For automated tests, continue using the existing test fixtures in `/tests/` for isolation and speed.

## Next Steps

1. **Start Development Server**: `python manage.py runserver`
2. **Access Admin Panel**: http://localhost:8000/admin/
3. **View API Documentation**: http://localhost:8000/api/docs/
4. **Test Endpoints**: Use created merchant accounts
5. **Monitor Logs**: Check transaction processing and KYC workflows

