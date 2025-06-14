from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from drf_spectacular.extensions import OpenApiSerializerExtension, OpenApiViewExtension
from drf_spectacular.plumbing import build_basic_type
from rest_framework import serializers

# Transaction schemas for OpenAPI documentation

qr_payment_example = {
    "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "amount": 150.00,
    "qr_code": "MERCHANT123:REF456:AMOUNT150.00",
    "reference": "QR_PAYMENT_001",
    "description": "Payment for groceries"
}

eft_payment_example = {
    "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "amount": 200.00,
    "bank_name": "First National Bank",
    "account_number": "12345678901234",
    "reference": "EFT_PAYMENT_001",
    "description": "Utility bill payment"
}

transaction_response_example = {
    "success": True,
    "message": "Payment processed successfully",
    "transaction": {
        "transaction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "amount": 150.00,
        "transaction_type": "payment",
        "status": "completed",
        "payment_method": "qr_code",
        "reference": "QR_PAYMENT_001",
        "description": "Payment for groceries",
        "created_at": "2025-06-11T15:30:45Z"
    },
    "status_code": 201
}

transaction_list_example = [
    {
        "transaction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "wallet": {
            "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "customer": {
                "customer_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "first_name": "John",
                "last_name": "Doe"
            }
        },
        "amount": 150.00,
        "transaction_type": "payment",
        "status": {
            "code": "completed",
            "name": "Completed"
        },
        "payment_method": {
            "code": "qr_code",
            "name": "QR Code Payment"
        },
        "reference": "QR_PAYMENT_001",
        "description": "Payment for groceries",
        "created_at": "2025-06-11T15:30:45Z",
        "updated_at": "2025-06-11T15:30:45Z"
    },
    {
        "transaction_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
        "wallet": {
            "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "customer": {
                "customer_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "first_name": "John",
                "last_name": "Doe"
            }
        },
        "amount": 200.00,
        "transaction_type": "payment",
        "status": {
            "code": "completed",
            "name": "Completed"
        },
        "payment_method": {
            "code": "eft",
            "name": "Electronic Fund Transfer"
        },
        "reference": "EFT_PAYMENT_001",
        "description": "Utility bill payment",
        "created_at": "2025-06-11T14:25:30Z",
        "updated_at": "2025-06-11T14:25:30Z"
    }
]

transaction_summary_example = {
    "total_transactions": 35,
    "transaction_counts": {
        "payments": 25,
        "deposits": 8,
        "withdrawals": 2
    },
    "transaction_volumes": {
        "payments": 12500.00,
        "deposits": 15000.00,
        "withdrawals": 3000.00,
        "total": 30500.00
    },
    "payment_methods": {
        "qr_code": {
            "name": "QR Code Payment",
            "count": 15,
            "volume": 7500.00
        },
        "eft": {
            "name": "Electronic Fund Transfer",
            "count": 10,
            "volume": 5000.00
        }
    },
    "recent_transactions": [
        {
            "transaction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "amount": 150.00,
            "transaction_type": "payment",
            "status": "completed",
            "created_at": "2025-06-11T15:30:45Z"
        },
        {
            "transaction_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
            "amount": 200.00,
            "transaction_type": "payment",
            "status": "completed",
            "created_at": "2025-06-11T14:25:30Z"
        }
    ]
}

# Schema extensions for transaction serializers
class TransactionSerializerExtension(OpenApiSerializerExtension):
    target_class = 'phantom_apps.transactions.serializers.TransactionSerializer'
    
    def map_serializer(self, auto_schema, direction):
        schema = auto_schema._map_serializer(self.target_class, direction, bypass_extensions=True)
        schema['example'] = transaction_list_example[0]
        return schema

class QRPaymentSerializerExtension(OpenApiSerializerExtension):
    target_class = 'phantom_apps.transactions.serializers.QRPaymentSerializer'
    
    def map_serializer(self, auto_schema, direction):
        schema = auto_schema._map_serializer(self.target_class, direction, bypass_extensions=True)
        schema['example'] = qr_payment_example
        return schema

class EFTPaymentSerializerExtension(OpenApiSerializerExtension):
    target_class = 'phantom_apps.transactions.serializers.EFTPaymentSerializer'
    
    def map_serializer(self, auto_schema, direction):
        schema = auto_schema._map_serializer(self.target_class, direction, bypass_extensions=True)
        schema['example'] = eft_payment_example
        return schema

class TransactionResponseSerializerExtension(OpenApiSerializerExtension):
    target_class = 'phantom_apps.transactions.serializers.TransactionResponseSerializer'
    
    def map_serializer(self, auto_schema, direction):
        schema = auto_schema._map_serializer(self.target_class, direction, bypass_extensions=True)
        schema['example'] = transaction_response_example
        return schema

