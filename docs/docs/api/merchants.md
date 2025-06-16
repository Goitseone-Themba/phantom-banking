---
sidebar_position: 3
title: Merchants
---

# Merchant API

The Merchant API allows you to manage merchant accounts, process payments, and access merchant-specific features.

## Register a Merchant

Register a new merchant account.

```http
POST /merchants/register/
```

### Request Body

```json
{
  "business_name": "Acme Corp",
  "business_type": "RETAIL",
  "registration_number": "REG123456",
  "tax_number": "TAX123456",
  "contact_email": "business@acme.com",
  "contact_phone": "+1234567890",
  "address": {
    "street": "123 Business St",
    "city": "Business City",
    "state": "Business State",
    "postal_code": "12345",
    "country": "US"
  }
}
```

### Response

```json
{
  "data": {
    "merchant_id": "mch_123456",
    "business_name": "Acme Corp",
    "status": "PENDING",
    "message": "Merchant registration successful. Awaiting verification."
  }
}
```

## Get Merchant Dashboard

Retrieve merchant dashboard data including key metrics.

```http
GET /merchants/dashboard/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Response

```json
{
  "data": {
    "merchant": {
      "merchant_id": "mch_123456",
      "business_name": "Acme Corp",
      "status": "ACTIVE",
      "created_at": "2024-03-20T12:00:00Z"
    },
    "total_wallets": 150,
    "total_transactions": 1250,
    "total_volume": 50000.00,
    "recent_transactions": [
      {
        "transaction_id": "txn_123",
        "amount": 100.00,
        "status": "COMPLETED",
        "created_at": "2024-03-20T11:30:00Z"
      }
    ]
  }
}
```

## Generate API Credentials

Generate new API credentials for merchant integration.

```http
POST /merchants/generate-api-credentials/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Response

```json
{
  "data": {
    "api_key": "pk_live_123456789",
    "api_secret": "sk_live_123456789",
    "created_at": "2024-03-20T12:00:00Z",
    "expires_at": "2025-03-20T12:00:00Z"
  }
}
```

## Get Merchant Balance

Retrieve merchant's current balance and transaction summary.

```http
GET /merchants/balance/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Response

```json
{
  "data": {
    "merchant_id": "mch_123456",
    "total_earnings": 50000.00,
    "pending_withdrawals": 5000.00,
    "available_balance": 45000.00,
    "last_updated": "2024-03-20T12:00:00Z"
  }
}
```

## Update Merchant Profile

Update merchant business information.

```http
PATCH /merchants/profile/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Request Body

```json
{
  "business_name": "Acme Corp Updated",
  "contact_email": "new@acme.com",
  "contact_phone": "+1987654321",
  "address": {
    "street": "456 New Business St",
    "city": "New Business City",
    "state": "New Business State",
    "postal_code": "54321",
    "country": "US"
  }
}
```

### Response

```json
{
  "data": {
    "merchant_id": "mch_123456",
    "business_name": "Acme Corp Updated",
    "status": "ACTIVE",
    "updated_at": "2024-03-20T12:00:00Z"
  }
}
```

## Get Merchant Transactions

Retrieve merchant's transaction history.

```http
GET /merchants/transactions/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Query Parameters

- `start_date` (optional): Filter transactions from this date (YYYY-MM-DD)
- `end_date` (optional): Filter transactions until this date (YYYY-MM-DD)
- `status` (optional): Filter by transaction status (COMPLETED, PENDING, FAILED)
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page (default: 20)

### Response

```json
{
  "data": {
    "transactions": [
      {
        "transaction_id": "txn_123",
        "amount": 100.00,
        "currency": "USD",
        "status": "COMPLETED",
        "type": "PAYMENT",
        "created_at": "2024-03-20T11:30:00Z",
        "customer": {
          "customer_id": "cust_123",
          "name": "John Doe"
        }
      }
    ],
    "pagination": {
      "total": 1250,
      "page": 1,
      "limit": 20,
      "pages": 63
    }
  }
}
```

## Get Merchant Analytics

Retrieve merchant's business analytics and insights.

```http
GET /merchants/analytics/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Query Parameters

- `period` (optional): Time period for analytics (day, week, month, year)
- `start_date` (optional): Start date for custom period
- `end_date` (optional): End date for custom period

### Response

```json
{
  "data": {
    "period": "month",
    "total_revenue": 50000.00,
    "transaction_count": 1250,
    "average_transaction": 40.00,
    "top_products": [
      {
        "product_id": "prod_123",
        "name": "Product A",
        "sales": 15000.00,
        "transactions": 300
      }
    ],
    "customer_metrics": {
      "total_customers": 500,
      "new_customers": 50,
      "repeat_customers": 450
    },
    "payment_methods": {
      "card": 60,
      "bank_transfer": 30,
      "mobile_money": 10
    }
  }
}
``` 