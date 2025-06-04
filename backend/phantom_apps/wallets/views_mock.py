"""
Mock implementations of wallet views for testing
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Wallet
from ..customers.models import Customer
from ..merchants.models import Merchant

# ----- Mock handlers for test purposes -----

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_wallet(request, customer_id):
    """Get a customer's wallet"""
    # Check if customer exists
    try:
        customer = get_object_or_404(Customer, customer_id=customer_id)
    except Http404:
        return Response({
            'error': True,
            'error_code': 'CUSTOMER_NOT_FOUND',
            'message': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if merchant has access to this customer
    merchant = request.user.merchant
    if customer.merchant.merchant_id != merchant.merchant_id:
        return Response({
            'error': True,
            'error_code': 'CUSTOMER_NOT_OWNED_BY_MERCHANT',
            'message': 'You do not have access to this customer'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get the wallet
    wallet = get_object_or_404(Wallet, customer=customer)
    
    # Return wallet data
    return Response({
        'success': True,
        'message': 'Customer wallet retrieved successfully',
        'wallet': {
            'wallet_id': str(wallet.wallet_id),
            'balance': str(wallet.balance),
            'currency': wallet.currency,
            'status': wallet.status,
            'customer': {
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone_number': customer.phone_number
            }
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_merchant_wallets(request, merchant_id):
    """List wallets for a merchant"""
    # Check merchant access
    if str(request.user.merchant.merchant_id) != str(merchant_id):
        return Response({
            'error': True,
            'error_code': 'PERMISSION_DENIED',
            'message': 'You do not have access to this merchant'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get query parameters
    status_filter = request.GET.get('status', 'active')
    customer_name = request.GET.get('customer_name', '')
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max page size 100
    
    # Get wallets
    wallets = Wallet.objects.filter(merchant_id=merchant_id)
    
    # Apply filters
    if status_filter != 'all':
        wallets = wallets.filter(status=status_filter)
    
    if customer_name:
        wallets = wallets.filter(customer__first_name__icontains=customer_name)
    
    # Total count
    total_count = wallets.count()
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    wallets = wallets[start:end]
    
    # Prepare response
    wallet_data = []
    for wallet in wallets:
        wallet_data.append({
            'wallet_id': str(wallet.wallet_id),
            'customer_name': wallet.customer.first_name,
            'balance': str(wallet.balance),
            'currency': wallet.currency,
            'status': wallet.status
        })
    
    # Return wallet list
    return Response({
        'success': True,
        'data': {
            'wallets': wallet_data,
            'pagination': {
                'total_count': total_count,
                'page_size': page_size,
                'current_page': page,
                'page_count': (total_count + page_size - 1) // page_size,
                'has_next': page * page_size < total_count,
                'has_previous': page > 1
            }
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_merchant_data_integrity(request, merchant_id):
    """Verify data integrity for a merchant"""
    # Check merchant access
    if str(request.user.merchant.merchant_id) != str(merchant_id):
        return Response({
            'error': True,
            'error_code': 'PERMISSION_DENIED',
            'message': 'You do not have access to this merchant'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get merchant
    merchant = get_object_or_404(Merchant, merchant_id=merchant_id)
    
    # Count customers and wallets
    customers_count = Customer.objects.filter(merchant=merchant).count()
    wallets_count = Wallet.objects.filter(merchant=merchant).count()
    
    # Check for customers without wallets
    customers_without_wallets = customers_count - wallets_count
    
    # Prepare integrity report
    issues = []
    if customers_without_wallets > 0:
        issues.append({
            'type': 'customers_without_wallets',
            'count': customers_without_wallets,
            'message': f'{customers_without_wallets} customers do not have wallets'
        })
    
    # Return integrity report
    return Response({
        'success': True,
        'integrity_report': {
            'merchant_id': str(merchant_id),
            'checks': {
                'customers_count': customers_count,
                'wallets_count': wallets_count,
                'customers_without_wallets': customers_without_wallets,
            },
            'summary': {
                'healthy': len(issues) == 0,
                'issues_count': len(issues),
            },
            'issues': issues
        }
    })

