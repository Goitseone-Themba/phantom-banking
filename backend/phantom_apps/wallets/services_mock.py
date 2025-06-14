"""
Mock implementations of service layer for wallets 
"""
from django.core.paginator import Paginator
from ..customers.models import Customer
from .models import Wallet

class CustomerAssociationService:
    """Mock implementation of CustomerAssociationService"""
    
    @staticmethod
    def get_customer_wallet(customer_id, authenticated_merchant):
        """Get wallet for a specific customer"""
        from django.shortcuts import get_object_or_404
        
        # Check if customer exists
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Check if merchant has access to this customer
        if customer.merchant.merchant_id != authenticated_merchant.merchant_id:
            from ..common.exceptions import CustomerNotOwnedError
            raise CustomerNotOwnedError(
                f"Customer {customer_id} does not belong to authenticated merchant"
            )
        
        # Get the wallet
        wallet = get_object_or_404(Wallet, customer=customer)
        
        return wallet
    
    @staticmethod
    def get_merchant_wallets(merchant, status_filter='active', customer_name_filter=None, page=1, page_size=20):
        """Get paginated list of wallets for a merchant"""
        # Get wallets for this merchant
        queryset = Wallet.objects.filter(merchant=merchant)
        
        # Apply status filter if not 'all'
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Apply customer name filter if provided
        if customer_name_filter:
            queryset = queryset.filter(
                customer__first_name__icontains=customer_name_filter
            )
        
        # Apply pagination
        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)
        
        # Prepare result
        result = {
            'wallets': current_page.object_list,
            'total_count': paginator.count,
            'page_count': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': current_page.has_next(),
            'has_previous': current_page.has_previous()
        }
        
        return result
    
    @staticmethod
    def verify_data_integrity(merchant):
        """Verify data integrity for a merchant"""
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

class WalletService:
    """Mock implementation of WalletService"""
    
    @staticmethod
    def create_or_get_wallet(merchant, customer_id):
        """Create or get a wallet for a customer"""
        from django.shortcuts import get_object_or_404
        from ..customers.models import Customer
        
        # Get customer
        customer = get_object_or_404(Customer, customer_id=customer_id, merchant=merchant)
        
        # Get or create wallet
        wallet, created = Wallet.objects.get_or_create(
            customer=customer,
            merchant=merchant,
            defaults={
                'balance': 0.00,
                'currency': 'BWP',
                'status': 'active',
                'is_frozen': False
            }
        )
        
        return wallet, created

