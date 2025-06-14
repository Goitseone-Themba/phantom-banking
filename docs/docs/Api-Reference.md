---
sidebar_position: 4
---


### Core Endpoints

#### 🏢 Merchants
# Register merchant
```
POST /api/v1/merchants/register/
{
  "business_name": "Furniture Store",
  "contact_email": "owner@furniturestore.com",
  "phone_number": "+26771234567",
  "business_registration": "BW123456"
}
```

# Get merchant dashboard
```
GET /api/v1/merchants/dashboard/
```

# Generate API credentials
```
POST /api/v1/merchants/generate-api-credentials/
```

#### 👤 Customers
# Create customer
```
POST /api/v1/customers/
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+26771234567",
  "email": "john@example.com"
}
```

# Get customer details
```
GET /api/v1/customers/{customer_id}/
```

#### 💰 Wallets

# Create phantom wallet for a customer
```
POST /api/v1/merchants/me/customers/{customer_id}/wallet/
{
  "initial_balance": 100.00,
  "currency": "BWP"
}
```

# Get customer wallet
```
GET /api/v1/customers/{customer_id}/wallet/
```

# List merchant wallets
```
GET /api/v1/merchants/{merchant_id}/wallets/
```

# Verify data integrity
```
GET /api/v1/merchants/{merchant_id}/integrity/
```

#### 💳 Transactions
# Process payment (API in development)
```
POST /api/v1/transactions/process/
{
  "wallet_id": "uuid-here",
  "amount": 100.00,
  "payment_channel": "qr_code",
  "reference": "TXN_001",
  "description": "Payment for goods"
}
```

# Get transaction history (API in development)
```
GET /api/v1/transactions/?wallet_id=uuid-here
```

# Get transaction details (API in development)
```
GET /api/v1/transactions/{transaction_id}/
```

#### 🛠️ Health Check
# Basic health check
```
GET /api/v1/health/
```

# Database health check
```
GET /api/v1/health/database/
```
