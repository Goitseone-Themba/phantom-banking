from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from drf_spectacular.openapi import AutoSchema
from rest_framework import serializers


# API Examples for documentation
QR_CODE_CREATE_EXAMPLES = [
    OpenApiExample(
        'Basic QR Code',
        description='Create a simple QR code for payment',
        value={
            "merchant_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "50.00",
            "description": "Coffee and pastry",
            "expires_in_minutes": 15
        },
        request_only=True,
    ),
    OpenApiExample(
        'QR Code with Reference',
        description='Create QR code with custom reference',
        value={
            "merchant_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "125.50",
            "description": "Monthly subscription",
            "reference": "SUB-2025-001",
            "expires_in_minutes": 30
        },
        request_only=True,
    ),
]

QR_CODE_RESPONSE_EXAMPLES = [
    OpenApiExample(
        'QR Code Created',
        description='Successful QR code creation response',
        value={
            "id": "456e7890-e89b-12d3-a456-426614174001",
            "qr_token": "QR1234ABCD5678EF",
            "amount": "50.00",
            "description": "Coffee and pastry",
            "reference": "",
            "merchant_name": "Café Delights",
            "status": "active",
            "expires_at": "2025-06-05T15:30:00Z",
            "created_at": "2025-06-05T15:15:00Z",
            "is_valid": True,
            "is_expired": False,
            "qr_data": "{\"token\":\"QR1234ABCD5678EF\",\"amount\":\"50.00\"}"
        },
        response_only=True,
    ),
]

QR_PAYMENT_EXAMPLES = [
    OpenApiExample(
        'Process QR Payment',
        description='Pay using QR code',
        value={
            "customer_phone": "71234567",
            "wallet_id": "789e0123-e89b-12d3-a456-426614174002"
        },
        request_only=True,
    ),
]

EFT_PAYMENT_EXAMPLES = [
    OpenApiExample(
        'FNB EFT Payment',
        description='Initiate EFT payment via FNB',
        value={
            "customer_phone": "71234567",
            "wallet_id": "789e0123-e89b-12d3-a456-426614174002",
            "amount": "500.00",
            "bank_code": "fnb",
            "account_number": "1234567890",
            "reference": "TOPUP-JUNE-2025"
        },
        request_only=True,
    ),
    OpenApiExample(
        'Standard Bank EFT',
        description='Initiate EFT payment via Standard Bank',
        value={
            "customer_phone": "72345678",
            "wallet_id": "890e1234-e89b-12d3-a456-426614174003",
            "amount": "1000.00",
            "bank_code": "standard",
            "account_number": "9876543210",
            "reference": "BUSINESS-TOPUP"
        },
        request_only=True,
    ),
]

EFT_RESPONSE_EXAMPLES = [
    OpenApiExample(
        'EFT Payment Initiated',
        description='Successful EFT payment initiation',
        value={
            "id": "abc12345-e89b-12d3-a456-426614174004",
            "amount": "500.00",
            "bank_code": "fnb",
            "account_number": "1234567890",
            "reference": "TOPUP-JUNE-2025",
            "status": "processing",
            "external_reference": "BNK-789123",
            "created_at": "2025-06-05T15:20:00Z",
            "processed_at": "2025-06-05T15:20:15Z",
            "completed_at": None,
            "customer_phone": "71234567",
            "customer_name": "John Doe",
            "wallet_balance": "250.00",
            "transaction_id": None,
            "response_data": {
                "status": "processing",
                "reference": "BNK-789123"
            }
        },
        response_only=True,
    ),
]

TRANSACTION_EXAMPLES = [
    OpenApiExample(
        'QR Payment Transaction',
        description='Completed QR code payment transaction',
        value={
            "id": "def45678-e89b-12d3-a456-426614174005",
            "transaction_type": "qr_payment",
            "amount": "50.00",
            "fee": "2.00",
            "net_amount": "50.00",
            "status": "completed",
            "reference": "",
            "description": "QR Payment: Coffee and pastry",
            "created_at": "2025-06-05T15:25:00Z",
            "completed_at": "2025-06-05T15:25:05Z",
            "customer_phone": "71234567",
            "customer_name": "John Doe",
            "merchant_name": "Café Delights",
            "from_wallet_balance": "948.00",
            "to_wallet_balance": None,
            "metadata": {
                "qr_token": "QR1234ABCD5678EF",
                "payment_method": "qr_code"
            }
        },
        response_only=True,
    ),
    OpenApiExample(
        'EFT Top-up Transaction',
        description='Completed EFT wallet top-up transaction',
        value={
            "id": "ghi78901-e89b-12d3-a456-426614174006",
            "transaction_type": "eft_topup",
            "amount": "500.00",
            "fee": "10.00",
            "net_amount": "490.00",
            "status": "completed",
            "reference": "TOPUP-JUNE-2025",
            "description": "EFT Top-up from fnb",
            "created_at": "2025-06-05T15:30:00Z",
            "completed_at": "2025-06-05T15:32:00Z",
            "customer_phone": "71234567",
            "customer_name": "John Doe",
            "merchant_name": None,
            "from_wallet_balance": None,
            "to_wallet_balance": "1490.00",
            "metadata": {
                "bank_code": "fnb",
                "external_reference": "BNK-789123",
                "payment_method": "eft"
            }
        },
        response_only=True,
    ),
]

WEBHOOK_EXAMPLES = [
    OpenApiExample(
        'Successful Payment Webhook',
        description='Bank webhook for successful payment',
        value={
            "reference": "BNK-789123",
            "status": "completed",
            "fee": "10.00",
            "timestamp": "2025-06-05T15:32:00Z",
            "transaction_id": "TXN-987654321"
        },
        request_only=True,
    ),
    OpenApiExample(
        'Failed Payment Webhook',
        description='Bank webhook for failed payment',
        value={
            "reference": "BNK-789124",
            "status": "failed",
            "error_code": "INSUFFICIENT_FUNDS",
            "error_message": "Account has insufficient funds",
            "timestamp": "2025-06-05T15:35:00Z"
        },
        request_only=True,
    ),
]


# Custom schema class for better documentation
class PaymentAPISchema(AutoSchema):
    """Custom schema for payment APIs"""
    
    def get_operation_id(self):
        """Generate operation IDs"""
        if hasattr(self.view, 'action'):
            action = self.view.action
        else:
            action = self.method.lower()
        
        model_name = getattr(self.view, 'queryset', None)
        if model_name is not None:
            model_name = model_name.model._meta.object_name.lower()
        else:
            model_name = self.view.__class__.__name__.lower().replace('view', '')
        
        return f"{model_name}_{action}"


# Error response examples
ERROR_EXAMPLES = {
    'validation_error': OpenApiExample(
        'Validation Error',
        description='Request data validation failed',
        value={
            "error": "Validation failed",
            "details": {
                "amount": ["Ensure this value is greater than or equal to 0.01."],
                "merchant_id": ["This field is required."]
            }
        },
        response_only=True,
        status_codes=['400']
    ),
    'not_found': OpenApiExample(
        'Resource Not Found',
        description='Requested resource was not found',
        value={
            "error": "QR code not found"
        },
        response_only=True,
        status_codes=['404']
    ),
    'insufficient_balance': OpenApiExample(
        'Insufficient Balance',
        description='Wallet has insufficient balance for transaction',
        value={
            "error": "Insufficient wallet balance"
        },
        response_only=True,
        status_codes=['400']
    ),
    'expired_qr': OpenApiExample(
        'Expired QR Code',
        description='QR code has expired or is no longer valid',
        value={
            "error": "QR code is invalid or expired"
        },
        response_only=True,
        status_codes=['400']
    )
}


# API Documentation strings
API_DESCRIPTIONS = {
    'qr_create': """
    Create a new QR code for payment acceptance.
    
    The QR code will contain payment information and can be scanned by customers
    to initiate payments. QR codes have a configurable expiration time.
    
    **Features:**
    - Configurable expiration time (1-1440 minutes)
    - Custom description and reference
    - Automatic token generation
    - Base64 encoded QR image generation
    
    **Use Cases:**
    - Point of sale payments
    - Online checkout
    - Bill payments
    - Service payments
    """,
    
    'qr_payment': """
    Process a payment using a QR code token.
    
    This endpoint validates the QR code, checks wallet balance, and processes
    the payment transaction. The QR code becomes invalid after successful payment.
    
    **Process:**
    1. Validate QR code token and expiration
    2. Verify customer and wallet
    3. Check sufficient balance (amount + fees)
    4. Create transaction record
    5. Update wallet balance
    6. Mark QR code as used
    
    **Fees:**
    - Standard transaction fee: P2.00
    """,
    
    'eft_initiate': """
    Initiate an EFT payment for wallet top-up.
    
    This endpoint starts the EFT payment process with the specified bank.
    The payment status can be tracked and will be updated via webhooks.
    
    **Supported Banks:**
    - FNB (fnb): Min P10, Max P50,000, Fee 2%
    - Standard Bank (standard): Min P10, Max P100,000, Fee 1.5%
    - Barclays (barclays): Min P5, Max P75,000, Fee 2.5%
    - Nedbank (nedbank): Min P10, Max P75,000, Fee 2%
    - Choppies Bank (choppies): Min P5, Max P25,000, Fee 3%
    
    **Process:**
    1. Validate customer and wallet
    2. Check amount limits for selected bank
    3. Create EFT payment record
    4. Submit to bank API
    5. Return processing status
    """,
    
    'eft_webhook': """
    Handle webhook notifications from bank systems.
    
    This endpoint receives status updates from bank APIs when EFT payments
    are completed, failed, or require additional processing.
    
    **Webhook Events:**
    - Payment completed successfully
    - Payment failed or declined
    - Payment cancelled by user
    - Additional verification required
    
    **Security:**
    - Webhook signatures should be verified (implementation dependent)
    - Idempotent processing to handle duplicate webhooks
    """,
    
    'transaction_list': """
    Retrieve a list of transactions with optional filtering.
    
    Returns paginated transaction history with support for filtering by
    customer, merchant, transaction type, and status.
    
    **Filters:**
    - customer_phone: Filter by customer phone number
    - merchant_id: Filter by merchant UUID
    - type: Filter by transaction type
    - status: Filter by transaction status
    
    **Pagination:**
    - Maximum 100 results per request
    - Results ordered by creation date (newest first)
    """
}


# Postman/Insomnia collection examples
POSTMAN_COLLECTION = {
    "info": {
        "name": "Phantom Banking Payment API",
        "description": "QR Code and EFT Payment API for Phantom Banking System",
        "version": "1.0.0"
    },
    "item": [
        {
            "name": "QR Code Payments",
            "item": [
                {
                    "name": "Create QR Code",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "merchant_id": "{{merchant_id}}",
                                "amount": "50.00",
                                "description": "Coffee purchase",
                                "expires_in_minutes": 15
                            })
                        },
                        "url": {
                            "raw": "{{base_url}}/api/payments/qr/create/",
                            "host": ["{{base_url}}"],
                            "path": ["api", "payments", "qr", "create", ""]
                        }
                    }
                },
                {
                    "name": "Get QR Code Details",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/api/payments/qr/{{qr_token}}/",
                            "host": ["{{base_url}}"],
                            "path": ["api", "payments", "qr", "{{qr_token}}", ""]
                        }
                    }
                },
                {
                    "name": "Process QR Payment",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "customer_phone": "{{customer_phone}}",
                                "wallet_id": "{{wallet_id}}"
                            })
                        },
                        "url": {
                            "raw": "{{base_url}}/api/payments/qr/{{qr_token}}/pay/",
                            "host": ["{{base_url}}"],
                            "path": ["api", "payments", "qr", "{{qr_token}}", "pay", ""]
                        }
                    }
                }
            ]
        },
        {
            "name": "EFT Payments",
            "item": [
                {
                    "name": "Initiate EFT Payment",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "customer_phone": "{{customer_phone}}",
                                "wallet_id": "{{wallet_id}}",
                                "amount": "500.00",
                                "bank_code": "fnb",
                                "account_number": "1234567890",
                                "reference": "TOPUP-2025"
                            })
                        },
                        "url": {
                            "raw": "{{base_url}}/api/payments/eft/initiate/",
                            "host": ["{{base_url}}"],
                            "path": ["api", "payments", "eft", "initiate", ""]
                        }
                    }
                },
                {
                    "name": "Check EFT Status",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/api/payments/eft/{{eft_payment_id}}/status/",
                            "host": ["{{base_url}}"],
                            "path": ["api", "payments", "eft", "{{eft_payment_id}}", "status", ""]
                        }
                    }
                }
            ]
        }
    ],
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:8000",
            "type": "string"
        },
        {
            "key": "merchant_id",
            "value": "",
            "type": "string"
        },
        {
            "key": "customer_phone",
            "value": "71000001",
            "type": "string"
        },
        {
            "key": "wallet_id",
            "value": "",
            "type": "string"
        },
        {
            "key": "qr_token",
            "value": "",
            "type": "string"
        },
        {
            "key": "eft_payment_id",
            "value": "",
            "type": "string"
        }
    ]
}


# cURL examples for testing
CURL_EXAMPLES = {
    'create_qr_code': '''
# Create QR Code
curl -X POST http://localhost:8000/api/payments/qr/create/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "merchant_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": "50.00",
    "description": "Test payment",
    "expires_in_minutes": 15
  }'
    ''',
    
    'get_qr_details': '''
# Get QR Code Details
curl -X GET http://localhost:8000/api/payments/qr/QR1234ABCD5678EF/
    ''',
    
    'process_qr_payment': '''
# Process QR Payment
curl -X POST http://localhost:8000/api/payments/qr/QR1234ABCD5678EF/pay/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "customer_phone": "71234567",
    "wallet_id": "789e0123-e89b-12d3-a456-426614174002"
  }'
    ''',
    
    'initiate_eft': '''
# Initiate EFT Payment
curl -X POST http://localhost:8000/api/payments/eft/initiate/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "customer_phone": "71234567",
    "wallet_id": "789e0123-e89b-12d3-a456-426614174002",
    "amount": "500.00",
    "bank_code": "fnb",
    "account_number": "1234567890",
    "reference": "TOPUP-2025"
  }'
    ''',
    
    'check_eft_status': '''
# Check EFT Payment Status
curl -X GET http://localhost:8000/api/payments/eft/abc12345-e89b-12d3-a456-426614174004/status/
    ''',
    
    'list_transactions': '''
# List Transactions
curl -X GET "http://localhost:8000/api/payments/transactions/?customer_phone=71234567&type=qr_payment"
    ''',
    
    'eft_webhook': '''
# EFT Webhook (from bank)
curl -X POST http://localhost:8000/api/payments/eft/webhook/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "reference": "BNK-789123",
    "status": "completed",
    "fee": "10.00",
    "timestamp": "2025-06-05T15:32:00Z"
  }'
    '''
}


# Testing checklist
TESTING_CHECKLIST = """
# Payment API Testing Checklist

## Setup
- [ ] Django server running on port 8000
- [ ] Database migrations applied
- [ ] Test data created using management command
- [ ] API documentation accessible at /api/schema/swagger-ui/

## QR Code Payment Testing
- [ ] Create QR code with valid merchant ID
- [ ] Create QR code with invalid merchant ID (should fail)
- [ ] Retrieve QR code details by token
- [ ] Generate QR code image
- [ ] Process payment with valid customer and wallet
- [ ] Process payment with insufficient balance (should fail)
- [ ] Process payment with expired QR code (should fail)
- [ ] Process payment with already used QR code (should fail)

## EFT Payment Testing
- [ ] Initiate EFT with valid bank code (fnb, standard, barclays)
- [ ] Initiate EFT with invalid bank code (should fail)
- [ ] Initiate EFT with amount below minimum (should fail)
- [ ] Initiate EFT with amount above maximum (should fail)
- [ ] Check EFT payment status
- [ ] Process webhook for completed payment
- [ ] Process webhook for failed payment
- [ ] Verify wallet balance updates after successful EFT

## Transaction API Testing
- [ ] List all transactions
- [ ] Filter transactions by customer phone
- [ ] Filter transactions by merchant ID
- [ ] Filter transactions by type (qr_payment, eft_topup)
- [ ] Filter transactions by status
- [ ] Verify pagination (max 100 results)

## Error Handling Testing
- [ ] Invalid UUIDs in requests
- [ ] Missing required fields
- [ ] Invalid phone numbers
- [ ] Negative amounts
- [ ] Non-existent resources
- [ ] Malformed JSON requests

## Performance Testing
- [ ] Concurrent QR code creation
- [ ] Concurrent payment processing
- [ ] Large transaction list queries
- [ ] Database query optimization verification

## Security Testing
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS prevention in responses
- [ ] Rate limiting (if implemented)
- [ ] Webhook signature verification (if implemented)
"""