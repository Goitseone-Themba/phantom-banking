from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# Swagger schema definitions for KYC API documentation

kyc_start_verification_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['first_name', 'last_name', 'date_of_birth', 'nationality', 'document_type', 'document_number', 'address_line_1', 'city', 'state_province', 'postal_code', 'country'],
    properties={
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s first name', example='John'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s last name', example='Doe'),
        'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date of birth (YYYY-MM-DD)', example='1990-01-01'),
        'nationality': openapi.Schema(type=openapi.TYPE_STRING, description='Nationality (ISO 3166-1 alpha-2 code)', example='BW'),
        'document_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['passport', 'id_card', 'driving_license'], description='Type of identity document'),
        'document_number': openapi.Schema(type=openapi.TYPE_STRING, description='Document number', example='BP123456789'),
        'address_line_1': openapi.Schema(type=openapi.TYPE_STRING, description='Primary address line', example='123 Main Street'),
        'address_line_2': openapi.Schema(type=openapi.TYPE_STRING, description='Secondary address line (optional)', example='Apt 4B'),
        'city': openapi.Schema(type=openapi.TYPE_STRING, description='City', example='Gaborone'),
        'state_province': openapi.Schema(type=openapi.TYPE_STRING, description='State or Province', example='South East'),
        'postal_code': openapi.Schema(type=openapi.TYPE_STRING, description='Postal/ZIP code', example='00000'),
        'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country (ISO 3166-1 alpha-2 code)', example='BW'),
    }
)

kyc_start_verification_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
        'session_url': openapi.Schema(type=openapi.TYPE_STRING, format='uri', description='Veriff session URL for user verification'),
        'session_id': openapi.Schema(type=openapi.TYPE_STRING, description='Veriff session ID'),
        'kyc_record': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Created KYC record details'
        )
    }
)

kyc_summary_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'kyc_status': openapi.Schema(type=openapi.TYPE_STRING, enum=['not_started', 'pending', 'in_progress', 'approved', 'rejected'], description='Current KYC status'),
        'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether KYC is verified'),
        'verification_level': openapi.Schema(type=openapi.TYPE_STRING, enum=['basic', 'enhanced', 'premium'], description='Verification level'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='KYC record creation timestamp'),
        'verified_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Verification completion timestamp'),
        'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Verification expiration timestamp'),
        'wallet_info': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'wallet_type': openapi.Schema(type=openapi.TYPE_STRING, description='Wallet type'),
                'balance': openapi.Schema(type=openapi.TYPE_STRING, description='Current balance'),
                'can_upgrade': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether wallet can be upgraded')
            }
        )
    }
)

# Swagger decorators for views
def kyc_start_verification_swagger():
    return swagger_auto_schema(
        operation_description="Start KYC verification process",
        operation_summary="Start KYC Verification",
        request_body=kyc_start_verification_request_schema,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Verification session created successfully",
                schema=kyc_start_verification_response_schema
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid input data or existing verification in progress",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                        'kyc_record': openapi.Schema(type=openapi.TYPE_OBJECT, description='Existing KYC record if applicable')
                    }
                )
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },
        tags=['KYC'],
    )

def kyc_summary_swagger():
    return swagger_auto_schema(
        operation_description="Get KYC verification summary for the current user",
        operation_summary="Get KYC Summary",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="KYC summary retrieved successfully",
                schema=kyc_summary_response_schema
            )
        },
        tags=['KYC'],
    )

def kyc_status_swagger():
    return swagger_auto_schema(
        operation_description="Get detailed KYC status and session information",
        operation_summary="Get KYC Status",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="KYC status retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'verification_level': openapi.Schema(type=openapi.TYPE_STRING),
                        'veriff_session_url': openapi.Schema(type=openapi.TYPE_STRING, format='uri'),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    }
                )
            )
        },
        tags=['KYC'],
    )

def veriff_webhook_swagger():
    return swagger_auto_schema(
        operation_description="Webhook endpoint for receiving Veriff verification results",
        operation_summary="Veriff Webhook",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='Veriff session ID'),
                'verification': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'decision': openapi.Schema(type=openapi.TYPE_STRING, enum=['approved', 'declined', 'resubmission_requested']),
                        'code': openapi.Schema(type=openapi.TYPE_STRING, description='Verification code'),
                        'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Reason for decision')
                    }
                )
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Webhook processed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['success'])
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid webhook data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['error'])
                    }
                )
            )
        },
        tags=['Webhooks'],
    )