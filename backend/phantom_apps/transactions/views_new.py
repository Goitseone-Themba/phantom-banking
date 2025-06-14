"""
New transaction API views for interoperable wallet system
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from .services_new import InteroperableTransactionService
from ..common.exceptions import (
    WalletNotFoundError,
    InsufficientFundsError,
    PhantomBankingException,
    PhantomBankingErrorCodes
)

logger = logging.getLogger('phantom_apps')


@extend_schema(
    tags=['Interoperable Transactions'],
    summary='Debit customer wallet',
    description='''
    Process a debit transaction from customer's wallet.
    
    **Access Required:** Merchant must have 'full' access to the wallet
    
    **Business Rules:**
    - Validates merchant access permissions
    - Checks sufficient balance before debiting
    - Records transaction with balance tracking
    - Updates wallet balance atomically
    ''',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'customer_phone': {'type': 'string', 'description': 'Customer phone number'},
                'amount': {'type': 'number', 'description': 'Amount to debit', 'minimum': 0.01},
                'description': {'type': 'string', 'description': 'Transaction description'},
                'reference': {'type': 'string', 'description': 'Transaction reference'},
                'transaction_type': {
                    'type': 'string',
                    'enum': ['merchant_debit', 'payment', 'withdrawal'],
                    'default': 'merchant_debit'
                }
            },
            'required': ['customer_phone', 'amount']
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debit_wallet(request):
    """
    Debit amount from customer's wallet
    
    URL: POST /api/v1/transactions/debit/
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
        amount = request.data.get('amount')
        description = request.data.get('description')
        reference = request.data.get('reference')
        transaction_type = request.data.get('transaction_type', 'merchant_debit')
        
        if not customer_phone or not amount:
            return Response({
                'error': True,
                'error_code': 'MISSING_REQUIRED_FIELDS',
                'message': 'Customer phone and amount are required',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process debit transaction
        transaction_obj = InteroperableTransactionService.process_wallet_debit(
            merchant=merchant,
            customer_phone=customer_phone,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference=reference
        )
        
        response_data = {
            'success': True,
            'message': 'Debit transaction processed successfully',
            'transaction': {
                'transaction_id': str(transaction_obj.transaction_id),
                'amount': str(transaction_obj.amount),
                'direction': transaction_obj.direction,
                'transaction_type': transaction_obj.transaction_type,
                'description': transaction_obj.description,
                'reference': transaction_obj.reference,
                'balance_before': str(transaction_obj.balance_before) if transaction_obj.balance_before else None,
                'balance_after': str(transaction_obj.balance_after) if transaction_obj.balance_after else None,
                'status': transaction_obj.status.code if transaction_obj.status else 'unknown',
                'created_at': transaction_obj.created_at.isoformat(),
                'completed_at': transaction_obj.completed_at.isoformat() if transaction_obj.completed_at else None
            },
            'status_code': 201
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except WalletNotFoundError as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except InsufficientFundsError as e:
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
        logger.error(f"Unexpected error in debit transaction: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.TRANSACTION_FAILED,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Interoperable Transactions'],
    summary='Credit customer wallet',
    description='''
    Process a credit transaction to customer's wallet.
    
    **Access Required:** Merchant must have 'credit_only' or 'full' access to the wallet
    
    **Business Rules:**
    - Validates merchant access permissions
    - Records transaction with balance tracking
    - Updates wallet balance atomically
    ''',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'customer_phone': {'type': 'string', 'description': 'Customer phone number'},
                'amount': {'type': 'number', 'description': 'Amount to credit', 'minimum': 0.01},
                'description': {'type': 'string', 'description': 'Transaction description'},
                'reference': {'type': 'string', 'description': 'Transaction reference'},
                'transaction_type': {
                    'type': 'string',
                    'enum': ['merchant_credit', 'topup', 'refund'],
                    'default': 'merchant_credit'
                }
            },
            'required': ['customer_phone', 'amount']
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def credit_wallet(request):
    """
    Credit amount to customer's wallet
    
    URL: POST /api/v1/transactions/credit/
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
        amount = request.data.get('amount')
        description = request.data.get('description')
        reference = request.data.get('reference')
        transaction_type = request.data.get('transaction_type', 'merchant_credit')
        
        if not customer_phone or not amount:
            return Response({
                'error': True,
                'error_code': 'MISSING_REQUIRED_FIELDS',
                'message': 'Customer phone and amount are required',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process credit transaction
        transaction_obj = InteroperableTransactionService.process_wallet_credit(
            merchant=merchant,
            customer_phone=customer_phone,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference=reference
        )
        
        response_data = {
            'success': True,
            'message': 'Credit transaction processed successfully',
            'transaction': {
                'transaction_id': str(transaction_obj.transaction_id),
                'amount': str(transaction_obj.amount),
                'direction': transaction_obj.direction,
                'transaction_type': transaction_obj.transaction_type,
                'description': transaction_obj.description,
                'reference': transaction_obj.reference,
                'balance_before': str(transaction_obj.balance_before) if transaction_obj.balance_before else None,
                'balance_after': str(transaction_obj.balance_after) if transaction_obj.balance_after else None,
                'status': transaction_obj.status.code if transaction_obj.status else 'unknown',
                'created_at': transaction_obj.created_at.isoformat(),
                'completed_at': transaction_obj.completed_at.isoformat() if transaction_obj.completed_at else None
            },
            'status_code': 201
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except WalletNotFoundError as e:
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
        logger.error(f"Unexpected error in credit transaction: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.TRANSACTION_FAILED,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Interoperable Transactions'],
    summary='Get customer transaction history',
    description='''
    Retrieve transaction history for a customer.
    
    **For Customers:** Returns all their transactions
    **For Merchants:** Returns only transactions they initiated (if they have access)
    
    **Access Control:**
    - Merchants can only see transactions from wallets they have access to
    - Merchants only see transactions they initiated
    ''',
    parameters=[
        OpenApiParameter('customer_phone', OpenApiTypes.STR, location=OpenApiParameter.PATH, description='Customer phone number'),
        OpenApiParameter('limit', OpenApiTypes.INT, description='Maximum number of transactions to return'),
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_transactions(request, customer_phone):
    """
    Get transaction history for a customer
    
    URL: GET /api/v1/transactions/customer/{customer_phone}/
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
        limit = min(int(request.GET.get('limit', 50)), 200)  # Max 200 transactions
        
        # Get transactions
        transactions = InteroperableTransactionService.get_customer_transactions(
            customer_phone=customer_phone,
            merchant=merchant,
            limit=limit
        )
        
        # Format transaction data
        transactions_data = []
        for transaction in transactions:
            transactions_data.append({
                'transaction_id': str(transaction.transaction_id),
                'amount': str(transaction.amount),
                'direction': transaction.direction,
                'transaction_type': transaction.transaction_type,
                'description': transaction.description,
                'reference': transaction.reference,
                'balance_before': str(transaction.balance_before) if transaction.balance_before else None,
                'balance_after': str(transaction.balance_after) if transaction.balance_after else None,
                'status': transaction.status.code if transaction.status else 'unknown',
                'merchant': {
                    'merchant_id': str(transaction.merchant.merchant_id) if transaction.merchant else None,
                    'business_name': transaction.merchant.business_name if transaction.merchant else None
                },
                'created_at': transaction.created_at.isoformat(),
                'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None
            })
        
        response_data = {
            'success': True,
            'message': 'Transaction history retrieved successfully',
            'data': {
                'customer_phone': customer_phone,
                'transactions': transactions_data,
                'total_returned': len(transactions_data),
                'limit_applied': limit
            },
            'access_note': 'Showing only transactions initiated by your merchant',
            'status_code': 200
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Unexpected error getting customer transactions: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.DATABASE_ERROR,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Interoperable Transactions'],
    summary='Get merchant transaction summary',
    description='''
    Get transaction summary statistics for the authenticated merchant.
    
    **Returns:**
    - Total transaction counts and amounts
    - Breakdown by transaction type
    - Recent transactions
    - Unique customers served
    ''',
    parameters=[
        OpenApiParameter('date_from', OpenApiTypes.DATE, description='Start date filter (YYYY-MM-DD)'),
        OpenApiParameter('date_to', OpenApiTypes.DATE, description='End date filter (YYYY-MM-DD)'),
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_merchant_transaction_summary(request):
    """
    Get transaction summary for the authenticated merchant
    
    URL: GET /api/v1/transactions/summary/
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
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Get transaction summary
        summary = InteroperableTransactionService.get_merchant_transaction_summary(
            merchant=merchant,
            date_from=date_from,
            date_to=date_to
        )
        
        response_data = {
            'success': True,
            'message': 'Transaction summary retrieved successfully',
            'data': {
                'merchant': {
                    'merchant_id': str(merchant.merchant_id),
                    'business_name': merchant.business_name
                },
                'date_range': {
                    'date_from': date_from,
                    'date_to': date_to
                },
                'summary': summary['summary'],
                'transaction_types': summary['transaction_types'],
                'recent_transactions': summary['recent_transactions']
            },
            'status_code': 200
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Unexpected error getting transaction summary: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.DATABASE_ERROR,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

