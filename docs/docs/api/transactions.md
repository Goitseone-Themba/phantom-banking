---
sidebar_position: 4
title: Transactions
---

# Transactions API

The Transactions API allows you to process payments, manage transactions, and handle different payment methods.

## Process QR Payment (Merchant)

Process a payment using a QR code (merchant authenticated).

```http
POST /transactions/merchant/qr-payment/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Request Body

```json
{
  "qr_token": "qr_123456",
  "amount": 100.00,
  "currency": "USD",
  "description": "Payment for order #123",
  "metadata": {
    "order_id": "order_123",
    "customer_id": "cust_123"
  }
}
```

### Response

```json
{
  "data": {
    "transaction_id": "txn_123",
    "status": "PENDING",
    "amount": 100.00,
    "currency": "USD",
    "created_at": "2024-03-20T12:00:00Z",
    "payment_url": "https://pay.phantombanking.com/txn_123"
  }
}
```

## Process EFT Payment (Merchant)

Process an Electronic Funds Transfer payment (merchant authenticated).

```http
POST /transactions/merchant/eft-payment/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Request Body

```json
{
  "amount": 100.00,
  "currency": "USD",
  "bank_account": {
    "account_number": "1234567890",
    "routing_number": "987654321",
    "account_type": "CHECKING"
  },
  "description": "Payment for order #123",
  "metadata": {
    "order_id": "order_123",
    "customer_id": "cust_123"
  }
}
```

### Response

```json
{
  "data": {
    "transaction_id": "txn_123",
    "status": "PENDING",
    "amount": 100.00,
    "currency": "USD",
    "created_at": "2024-03-20T12:00:00Z",
    "estimated_completion": "2024-03-21T12:00:00Z"
  }
}
```

## Create QR Code

Generate a new QR code for payments.

```http
POST /transactions/qr/create/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Request Body

```json
{
  "amount": 100.00,
  "currency": "USD",
  "description": "Payment for order #123",
  "expires_at": "2024-03-21T12:00:00Z",
  "metadata": {
    "order_id": "order_123"
  }
}
```

### Response

```json
{
  "data": {
    "qr_token": "qr_123456",
    "qr_image_url": "https://api.phantombanking.com/qr/qr_123456/image",
    "payment_url": "https://pay.phantombanking.com/qr/qr_123456",
    "expires_at": "2024-03-21T12:00:00Z"
  }
}
```

## Get QR Code Details

Retrieve details of a specific QR code.

```http
GET /transactions/qr/{qr_token}/
```

### Response

```json
{
  "data": {
    "qr_token": "qr_123456",
    "amount": 100.00,
    "currency": "USD",
    "description": "Payment for order #123",
    "status": "ACTIVE",
    "created_at": "2024-03-20T12:00:00Z",
    "expires_at": "2024-03-21T12:00:00Z",
    "metadata": {
      "order_id": "order_123"
    }
  }
}
```

## Process QR Payment (Public)

Process a payment using a QR code (public endpoint).

```http
POST /transactions/qr/{qr_token}/pay/
```

### Request Body

```json
{
  "payment_method": "CARD",
  "card_details": {
    "number": "4242424242424242",
    "exp_month": 12,
    "exp_year": 2025,
    "cvc": "123"
  }
}
```

### Response

```json
{
  "data": {
    "transaction_id": "txn_123",
    "status": "COMPLETED",
    "amount": 100.00,
    "currency": "USD",
    "created_at": "2024-03-20T12:00:00Z",
    "receipt_url": "https://api.phantombanking.com/receipts/txn_123"
  }
}
```

## Initiate EFT Payment

Initiate an Electronic Funds Transfer payment (public endpoint).

```http
POST /transactions/eft/initiate/
```

### Request Body

```json
{
  "amount": 100.00,
  "currency": "USD",
  "bank_account": {
    "account_number": "1234567890",
    "routing_number": "987654321",
    "account_type": "CHECKING"
  },
  "description": "Payment for order #123"
}
```

### Response

```json
{
  "data": {
    "transaction_id": "txn_123",
    "status": "PENDING",
    "amount": 100.00,
    "currency": "USD",
    "created_at": "2024-03-20T12:00:00Z",
    "estimated_completion": "2024-03-21T12:00:00Z"
  }
}
```

## Get Transaction Status

Check the status of a transaction.

```http
GET /transactions/{transaction_id}/
```

### Response

```json
{
  "data": {
    "transaction_id": "txn_123",
    "status": "COMPLETED",
    "amount": 100.00,
    "currency": "USD",
    "type": "PAYMENT",
    "payment_method": "CARD",
    "created_at": "2024-03-20T12:00:00Z",
    "completed_at": "2024-03-20T12:00:05Z",
    "description": "Payment for order #123",
    "metadata": {
      "order_id": "order_123"
    }
  }
}
```

## Get Transaction List

Retrieve a list of transactions with filtering and pagination.

```http
GET /transactions/
```

### Query Parameters

- `start_date` (optional): Filter transactions from this date (YYYY-MM-DD)
- `end_date` (optional): Filter transactions until this date (YYYY-MM-DD)
- `status` (optional): Filter by transaction status (COMPLETED, PENDING, FAILED)
- `type` (optional): Filter by transaction type (PAYMENT, REFUND, TRANSFER)
- `payment_method` (optional): Filter by payment method (CARD, EFT, QR)
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page (default: 20)

### Response

```json
{
  "data": {
    "transactions": [
      {
        "transaction_id": "txn_123",
        "status": "COMPLETED",
        "amount": 100.00,
        "currency": "USD",
        "type": "PAYMENT",
        "payment_method": "CARD",
        "created_at": "2024-03-20T12:00:00Z",
        "description": "Payment for order #123"
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

## Get Payment Analytics

Retrieve payment analytics and insights.

```http
GET /transactions/analytics/
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
    "total_volume": 50000.00,
    "transaction_count": 1250,
    "average_transaction": 40.00,
    "success_rate": 98.5,
    "payment_methods": {
      "card": {
        "volume": 30000.00,
        "count": 750,
        "success_rate": 99.0
      },
      "eft": {
        "volume": 15000.00,
        "count": 300,
        "success_rate": 97.5
      },
      "qr": {
        "volume": 5000.00,
        "count": 200,
        "success_rate": 99.5
      }
    },
    "hourly_distribution": {
      "00:00": 5,
      "01:00": 3,
      // ... other hours
    }
  }
}
``` 