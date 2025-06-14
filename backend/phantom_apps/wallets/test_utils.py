"""
Helper functions for wallet tests
"""
from .models import Wallet
from ..customers.models import Customer

def get_mock_merchant_wallets(merchant, status_filter='active', customer_name_filter=None, page=1, page_size=20):
    """Get wallets for a merchant with simple pagination (no Paginator needed)"""
    # Get wallets for this merchant
    wallets = Wallet.objects.filter(merchant=merchant)
    
    # Apply status filter if not 'all'
    if status_filter != 'all':
        wallets = wallets.filter(status=status_filter)
    
    # Apply customer name filter if provided
    if customer_name_filter:
        wallets = wallets.filter(
            customer__first_name__icontains=customer_name_filter
        )
    
    # Count before slicing
    total_count = wallets.count()
    
    # Calculate pagination values
    page_count = (total_count + page_size - 1) // page_size if total_count > 0 else 1
    has_next = page < page_count
    has_previous = page > 1
    
    # Apply pagination manually
    start = (page - 1) * page_size
    end = start + page_size
    wallets = wallets[start:end]
    
    # Prepare result
    result = {
        'wallets': wallets,
        'total_count': total_count,
        'page_count': page_count,
        'current_page': page,
        'page_size': page_size,
        'has_next': has_next,
        'has_previous': has_previous
    }
    
    return result

def get_mock_data_integrity(merchant):
    """Verify data integrity for a merchant - simplified version"""
    # Count customers and wallets
    customers_count = Customer.objects.filter(merchant=merchant).count()
    wallets_count = Wallet.objects.filter(merchant=merchant).count()
    
    # Find customers without wallets
    customers_without_wallets = customers_count - wallets_count
    
    # Prepare issues list
    issues = []
    if customers_without_wallets > 0:
        issues.append({
            'type': 'customers_without_wallets',
            'count': customers_without_wallets,
            'message': f'{customers_without_wallets} customers do not have wallets'
        })
    
    # Prepare report
    integrity_report = {
        'merchant_id': str(merchant.merchant_id),  # Convert UUID to string
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
    
    return integrity_report

