"""
New API views for interoperable wallet system
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from .services_new import InteroperableWalletService
from ..transactions.services_new import InteroperableTransactionService
from ..common.exceptions import (
    CustomerNotFoundError,
    WalletNotFoundError,
    PhantomBankingException,
    PhantomBankingErrorCodes
)

logger = logging.getLogger('phantom_apps')


@extend_schema(
    tags=['Interoperable Wallets'],
    summary='Create or access customer wallet (New Business Model)',
    description='''
    Create a wallet for a customer or get access to existing wallet.
    
    **New Business Rules:**
    - One wallet per customer globally (not per merchant)
    - Any merchant can access existing wallets (with proper permissions)
    - Merchants can create wallets for new customers
    - Access levels: full, credit_only, view_only
    
    **Returns:**
    - Wallet information
    - Access level granted to the merchant
    - Whether wallet was newly created
    ''',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'customer_phone': {'type': 'string', 'description': 'Customer phone number'},
                'customer_info': {
                    'type': 'object',
                    'properties': {
                        'first_name': {'type': 'string'},
                        'last_name': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                    },
                    'description': 'Customer info if creating new customer (optional)'
                }
            },
            'required': ['customer_phone']
        }
    },
    responses={
        201: {
            'description': 'Wallet created successfully',
            'example': {
                'success': True,
                'message': 'Wallet created successfully',
                'wallet_created': True,
                'access_granted': True,
                'wallet': {
                    'wallet_id': 'uuid-here',
                    'balance': '0.00',
                    'currency': 'BWP',
                    'status': 'active'
                },
                'access_info': {
                    'access_type': 'full',
                    'can_debit': True,
                    'can_credit': True,
                    'can_view': True
                }
            }
        },
        200: {
            'description': 'Access granted to existing wallet',
            'example': {
                'success': True,
                'message': 'Access granted to existing wallet',
                'wallet_created': False,
                'access_granted': True,
                'wallet': {
                    'wallet_id': 'uuid-here',
                    'balance': '150.00',
                    'currency': 'BWP',
                    'status': 'active'
                },
                'access_info': {
                    'access_type': 'full',
                    'can_debit': True,
                    'can_credit': True,
                    'can_view': True
                }
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_access_wallet(request):
    """
    Create wallet for customer or get access to existing wallet
    
    URL: POST /api/v1/wallets/create-or-access/
    """
    try:
        # Extract merchant from JWT token
        try:
            merchant = request.user.merchant
        except AttributeError:
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.MERCHANT_NOT_FOUND,
                'message': 'No merchant associated with authenticated user',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate request data
        customer_phone = request.data.get('customer_phone')
        
        if not customer_phone:
            return Response({
                'error': True,
                'error_code': 'MISSING_CUSTOMER_PHONE',
                'message': 'Customer phone number is required',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get wallet with access info
        wallet, wallet_created, access_info = InteroperableWalletService.create_or_get_wallet(
            merchant=merchant,
            customer_phone_or_id=customer_phone
        )
        
        # Determine message based on access status
        if wallet_created:
            message = 'Wallet created successfully with automatic full access'
        elif access_info.get('has_access'):
            message = f'Existing wallet found. You have {access_info.get("access_type", "unknown")} access'
        else:
            message = 'Wallet found but no access. Contact administrator for access.'
        
        response_data = {
            'success': True,
            'message': message,
            'wallet_created': wallet_created,
            'has_access': access_info.get('has_access', False),
            'wallet': {
                'wallet_id': str(wallet.wallet_id),
                'balance': str(wallet.balance) if access_info.get('can_view', False) else 'Hidden',
                'currency': wallet.currency,
                'status': wallet.status,
                'customer': {
                    'first_name': wallet.customer.first_name,
                    'last_name': wallet.customer.last_name,
                    'phone_number': wallet.customer.phone_number
                }
            },
            'access_info': access_info,
            'admin_note': 'Access permissions are controlled by administrators only.',
            'status_code': 201 if wallet_created else 200
        }
        
        response_status = status.HTTP_201_CREATED if wallet_created else status.HTTP_200_OK
        return Response(response_data, status=response_status)
        
    except CustomerNotFoundError as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except PhantomBankingException as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except Exception as e:
        logger.error(f"Unexpected error in wallet creation/access: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.DATABASE_ERROR,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Interoperable Wallets'],
    summary='List accessible wallets for merchant',
    description='''
    Get list of wallets that the authenticated merchant has access to.
    
    **Access Control:**
    - Merchants only see wallets they have been granted access to
    - Access types determine what operations are possible
    - Includes access metadata for each wallet
    ''',
    parameters=[
        OpenApiParameter('status', OpenApiTypes.STR, description='Filter by wallet status'),
        OpenApiParameter('customer_name', OpenApiTypes.STR, description='Filter by customer name'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number'),
        OpenApiParameter('page_size', OpenApiTypes.INT, description='Items per page'),
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_accessible_wallets(request):
    """
    List wallets accessible by the authenticated merchant
    
    URL: GET /api/v1/wallets/accessible/
    """
    try:
        # Extract merchant from JWT token
        try:
            merchant = request.user.merchant
        except AttributeError:
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.MERCHANT_NOT_FOUND,
                'message': 'No merchant associated with authenticated user',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        status_filter = request.GET.get('status', 'active')
        customer_name_filter = request.GET.get('customer_name')
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # Get accessible wallets
        result = InteroperableWalletService.get_accessible_wallets(
            merchant=merchant,
            status_filter=status_filter,
            customer_name_filter=customer_name_filter,
            page=page,
            page_size=page_size
        )
        
        # Format wallet data
        wallets_data = []
        for wallet in result['wallets']:
            wallet_id_str = str(wallet.wallet_id)
            access_info = result['access_info'].get(wallet_id_str, {})
            
            wallets_data.append({
                'wallet_id': wallet_id_str,
                'balance': str(wallet.balance),
                'currency': wallet.currency,
                'status': wallet.status,
                'customer': {
                    'first_name': wallet.customer.first_name,
                    'last_name': wallet.customer.last_name,
                    'phone_number': wallet.customer.phone_number
                },
                'access_info': access_info,
                'created_at': wallet.created_at.isoformat()
            })
        
        response_data = {
            'success': True,
            'message': 'Accessible wallets retrieved successfully',
            'data': {
                'wallets': wallets_data,
                'pagination': {
                    'total_count': result['total_count'],
                    'page_count': result['page_count'],
                    'current_page': result['current_page'],
                    'page_size': result['page_size'],
                    'has_next': result['has_next'],
                    'has_previous': result['has_previous']
                }
            },
            'filters_applied': {
                'status': status_filter,
                'customer_name': customer_name_filter
            },
            'status_code': 200
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Unexpected error listing accessible wallets: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.DATABASE_ERROR,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Interoperable Wallets'],
    summary='Get customer wallet by phone number',
    description='''
    Retrieve a customer's wallet information by phone number.
    
    **Access Control:**
    - Merchant must have access to the customer's wallet
    - Returns access level information
    - Shows current balance and wallet status
    ''',
    parameters=[
        OpenApiParameter('customer_phone', OpenApiTypes.STR, location=OpenApiParameter.PATH, description='Customer phone number'),
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallet_by_customer_phone(request, customer_phone):
    """
    Get wallet information for a customer by phone number
    
    URL: GET /api/v1/wallets/customer/{customer_phone}/
    """
    try:
        # Extract merchant from JWT token
        try:
            merchant = request.user.merchant
        except AttributeError:
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.MERCHANT_NOT_FOUND,
                'message': 'No merchant associated with authenticated user',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get wallet and access info
        result = InteroperableWalletService.get_customer_wallet_by_phone(
            customer_phone=customer_phone,
            authenticated_merchant=merchant
        )
        
        wallet = result['wallet']
        access_info = result['access_info']
        
        # Check if merchant has access
        if access_info and not access_info['has_access']:
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.PERMISSION_DENIED,
                'message': 'You do not have access to this wallet',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)
        
        response_data = {
            'success': True,
            'message': 'Wallet retrieved successfully',
            'wallet': {
                'wallet_id': str(wallet.wallet_id),
                'balance': str(wallet.balance) if access_info and access_info['can_view'] else 'Hidden',
                'currency': wallet.currency,
                'status': wallet.status,
                'customer': {
                    'first_name': wallet.customer.first_name,
                    'last_name': wallet.customer.last_name,
                    'phone_number': wallet.customer.phone_number
                },
                'created_at': wallet.created_at.isoformat()
            },
            'access_info': access_info,
            'status_code': 200
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except CustomerNotFoundError as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except WalletNotFoundError as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except Exception as e:
        logger.error(f"Unexpected error getting wallet by phone: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.DATABASE_ERROR,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

