# Phantom Payment System

A Django-based payment processing system that supports QR code payments and EFT (Electronic Funds Transfer) transactions.

## Features

- **QR Code Payments**: Generate scannable QR codes for instant payments
- **EFT Processing**: Handle bank transfers to digital wallets
- **Transaction Management**: Complete audit trail and history
- **Real-time Processing**: Instant QR payments with async EFT processing
- **Admin Interface**: Django admin panel for system management
- **API Documentation**: Swagger/OpenAPI documentation

## Prerequisites

- Python 3.8+
- Django
- SQLite (default) or PostgreSQL
- pip package manager

## Quick Start

### 1. Installation

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# For specific app migrations
python manage.py makemigrations transactions
python manage.py migrate
```

### 3. Create Admin User

```bash
python manage.py createsuperuser
```

**Recommended credentials for testing:**
- Username: `admin`
- Email: `admin@phantom.com`
- Password: `admin123`

### 4. Generate Test Data

```bash
# Create sample customers, merchants, and wallets
python manage.py create_test_data --customers 5 --merchants 3
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

Your server will be available at: **http://localhost:8000/**

## API Endpoints

### Admin Panel
- **URL**: http://localhost:8000/admin/
- **Purpose**: Manage merchants, customers, wallets, and transactions

### API Documentation
- **URL**: http://localhost:8000/api/schema/swagger-ui/
- **Purpose**: Interactive API documentation and testing

## Testing the Payment System

### Test 1: Create a QR Code

```bash
curl -X POST http://localhost:8000/api/payments/qr/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "YOUR_MERCHANT_ID_FROM_ADMIN",
    "amount": "25.50",
    "description": "Coffee and sandwich",
    "expires_in_minutes": 30
  }'
```

**Expected Response:**
```json
{
  "id": "abc123...",
  "qr_token": "QR1234ABCD5678EF",
  "amount": "25.50",
  "description": "Coffee and sandwich",
  "merchant_name": "Test Merchant 1",
  "status": "active",
  "is_valid": true
}
```

### Test 2: View QR Code Image

Visit: `http://localhost:8000/api/payments/qr/QR1234ABCD5678EF/image/`

This will return a JSON response with a base64-encoded QR code image.

### Test 3: Process QR Payment

```bash
curl -X POST http://localhost:8000/api/payments/qr/QR1234ABCD5678EF/pay/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "71000001",
    "wallet_id": "YOUR_WALLET_ID_FROM_ADMIN"
  }'
```

### Test 4: Initiate EFT Payment

```bash
curl -X POST http://localhost:8000/api/payments/eft/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "71000001",
    "wallet_id": "YOUR_WALLET_ID_FROM_ADMIN",
    "amount": "100.00",
    "bank_code": "fnb",
    "account_number": "1234567890",
    "reference": "TEST-TOPUP"
  }'
```

### Test 5: Simulate Bank Webhook

```bash
# Use the external_reference from the EFT response
curl -X POST http://localhost:8000/api/payments/eft/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "reference": "BNK-123456",
    "status": "completed",
    "fee": "5.00",
    "timestamp": "2025-06-05T15:32:00Z"
  }'
```

## Quick Demo Flow

1. **Access Admin Panel**
   - Visit: http://localhost:8000/admin/
   - Login with `admin/admin123`
   - Note down a Merchant ID and Wallet ID from the admin interface

2. **Explore API Documentation**
   - Visit: http://localhost:8000/api/schema/swagger-ui/
   - Try the "Create QR Code" endpoint with the merchant ID from step 1

3. **Test QR Payment Workflow**
   - Create QR code → Receive QR token
   - View QR image → See the actual QR code
   - Process payment → Complete the transaction

4. **Test EFT Payment Workflow**
   - Initiate EFT → Receive payment ID
   - Check status → Monitor processing status
   - Send webhook → Complete the payment

## Troubleshooting

### Migration Issues

If migrations fail, try resetting them:

```bash
# Delete and recreate migrations
rm backend/phantom_apps/transactions/migrations/*.py
python manage.py makemigrations transactions
python manage.py migrate
```

### Package Installation Issues

If packages fail to install, try individual installations:

```bash
pip install qrcode
pip install pillow
pip install drf-spectacular
```

### Import Errors

Make sure your `phantom_apps` directory has `__init__.py` files in all subdirectories:

```
phantom_apps/
├── __init__.py
├── transactions/
│   ├── __init__.py
│   ├── models.py
│   └── ...
└── ...
```

### Common Issues

- **Database locked**: Stop the server and restart
- **Port already in use**: Use `python manage.py runserver 8001` for a different port
- **Missing dependencies**: Check `requirements.txt` and reinstall packages

## What You'll Experience

- **QR Code API**: Generate scannable QR codes for payments
- **EFT API**: Process bank transfers to digital wallets  
- **Transaction History**: Complete audit trail of all payments
- **Real-time Processing**: Instant QR payments with asynchronous EFT processing
- **Comprehensive Testing**: Full test suite for all payment flows

## Project Structure

```
phantom-payment-system/
├── backend/
│   ├── phantom_apps/
│   │   ├── transactions/
│   │   └── ...
│   ├── manage.py
│   └── requirements.txt
├── README.md
└── ...
```


## Support

For issues and questions, please check the troubleshooting section above or create an issue in the project repository.