# phantom_apps/analytics/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from datetime import datetime, timedelta
from decimal import Decimal
import json
from collections import defaultdict
import random

from .models import AnalyticsDataGenerator, MockCustomer, MockTransaction, MockMerchant

class AnalyticsDataManager:
    """Manage generated data across requests"""
    _customers = None
    _transactions = None
    _merchants = None
    
    @classmethod
    def get_customers(cls):
        if cls._customers is None:
            cls._customers = AnalyticsDataGenerator.generate_customers(100)
        return cls._customers
    
    @classmethod
    def get_transactions(cls):
        if cls._transactions is None:
            customers = cls.get_customers()
            cls._transactions = AnalyticsDataGenerator.generate_transactions(customers, 1000)
        return cls._transactions
    
    @classmethod
    def get_merchants(cls):
        if cls._merchants is None:
            cls._merchants = AnalyticsDataGenerator.generate_merchants(50)
        return cls._merchants
    
    @classmethod
    def get_customer_by_id(cls, customer_id):
        customers = cls.get_customers()
        for customer in customers:
            if customer.customer_id == customer_id:
                return customer
        return None
    
    @classmethod
    def get_customer_transactions(cls, customer_id):
        transactions = cls.get_transactions()
        return [t for t in transactions if t.customer_id == customer_id]

@staff_member_required
def analytics_dashboard(request):
    """Main analytics dashboard view"""
    
    # Get generated data
    customers = AnalyticsDataManager.get_customers()
    transactions = AnalyticsDataManager.get_transactions()
    merchants = AnalyticsDataManager.get_merchants()
    
    # Calculate summary statistics
    total_customers = len(customers)
    total_transactions = len(transactions)
    total_revenue = sum([t.amount for t in transactions])
    avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
    
    # Monthly revenue data for chart
    monthly_data = defaultdict(Decimal)
    for transaction in transactions:
        month_key = transaction.transaction_date.strftime('%Y-%m')
        monthly_data[month_key] += transaction.amount
    
    # Sort by month and get last 12 months
    sorted_months = sorted(monthly_data.keys())[-12:]
    monthly_revenue = [{'month': month, 'revenue': float(monthly_data[month])} for month in sorted_months]
    
    # Top customers by spending
    customer_spending = defaultdict(Decimal)
    for transaction in transactions:
        customer_spending[transaction.customer_id] += transaction.amount
    
    top_customers = []
    for customer in customers:
        spending = customer_spending.get(customer.customer_id, Decimal('0'))
        if spending > 0:
            top_customers.append({
                'customer': customer,
                'total_spending': spending
            })
    
    top_customers = sorted(top_customers, key=lambda x: x['total_spending'], reverse=True)[:10]
    
    # Category breakdown
    category_data = defaultdict(Decimal)
    for transaction in transactions:
        category_data[transaction.category] += transaction.amount
    
    category_breakdown = [{'category': k, 'amount': float(v)} for k, v in category_data.items()]
    
    # Risk analysis
    high_risk_customers = [c for c in customers if c.risk_score > 70]
    medium_risk_customers = [c for c in customers if 30 <= c.risk_score <= 70]
    low_risk_customers = [c for c in customers if c.risk_score < 30]
    
    context = {
        'total_customers': total_customers,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'avg_transaction_value': avg_transaction_value,
        'monthly_revenue': json.dumps(monthly_revenue),
        'top_customers': top_customers,
        'category_breakdown': json.dumps(category_breakdown),
        'customers': customers[:20],  # Show first 20 customers
        'high_risk_count': len(high_risk_customers),
        'medium_risk_count': len(medium_risk_customers),
        'low_risk_count': len(low_risk_customers),
        'merchants': merchants[:10],  # Show top 10 merchants
    }
    
    return render(request, 'analytics/dashboard.html', context)

@staff_member_required
def customer_detail(request, customer_id):
    """Detailed customer analytics view"""
    
    # Get customer data
    customer = AnalyticsDataManager.get_customer_by_id(customer_id)
    if not customer:
        return render(request, 'analytics/customer_detail.html', {'error': 'Customer not found'})
    
    # Get customer transactions
    transactions = AnalyticsDataManager.get_customer_transactions(customer_id)
    
    # Calculate customer statistics
    total_spent = sum([t.amount for t in transactions])
    transaction_count = len(transactions)
    avg_transaction = total_spent / transaction_count if transaction_count > 0 else 0
    
    # Monthly spending pattern
    monthly_spending = defaultdict(Decimal)
    for transaction in transactions:
        month_key = transaction.transaction_date.strftime('%Y-%m')
        monthly_spending[month_key] += transaction.amount
    
    # Sort by month and get last 12 months
    sorted_months = sorted(monthly_spending.keys())[-12:]
    monthly_data = [{'month': month, 'amount': float(monthly_spending[month])} for month in sorted_months]
    
    # Category breakdown for this customer
    category_spending = defaultdict(Decimal)
    for transaction in transactions:
        category_spending[transaction.category] += transaction.amount
    
    category_data = [{'category': k, 'amount': float(v)} for k, v in category_spending.items()]
    
    # Recent transactions (last 10)
    recent_transactions = sorted(transactions, key=lambda x: x.transaction_date, reverse=True)[:10]
    
    # Merchant preferences
    merchant_spending = defaultdict(Decimal)
    for transaction in transactions:
        merchant_spending[transaction.merchant] += transaction.amount
    
    top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context = {
        'customer': customer,
        'total_spent': total_spent,
        'transaction_count': transaction_count,
        'avg_transaction': avg_transaction,
        'monthly_data': json.dumps(monthly_data),
        'category_data': json.dumps(category_data),
        'recent_transactions': recent_transactions,
        'top_merchants': top_merchants,
        'risk_level': 'High' if customer.risk_score > 70 else 'Medium' if customer.risk_score > 30 else 'Low',
    }
    
    return render(request, 'analytics/customer_detail.html', context)

@staff_member_required
def analytics_api_data(request):
    """API endpoint for chart data"""
    
    data_type = request.GET.get('type', 'revenue')
    
    if data_type == 'revenue':
        transactions = AnalyticsDataManager.get_transactions()
        monthly_data = defaultdict(Decimal)
        
        for transaction in transactions:
            month_key = transaction.transaction_date.strftime('%Y-%m')
            monthly_data[month_key] += transaction.amount
        
        # Convert to list format for charts
        chart_data = []
        sorted_months = sorted(monthly_data.keys())[-12:]
        
        for month in sorted_months:
            chart_data.append({
                'month': month,
                'revenue': float(monthly_data[month])
            })
        
        return JsonResponse({'data': chart_data})
    
    elif data_type == 'categories':
        transactions = AnalyticsDataManager.get_transactions()
        category_data = defaultdict(Decimal)
        
        for transaction in transactions:
            category_data[transaction.category] += transaction.amount
        
        chart_data = [{'category': k, 'amount': float(v)} for k, v in category_data.items()]
        
        return JsonResponse({'data': chart_data})
    
    elif data_type == 'customers':
        customers = AnalyticsDataManager.get_customers()
        transactions = AnalyticsDataManager.get_transactions()
        
        customer_data = defaultdict(lambda: {'spending': Decimal('0'), 'transactions': 0})
        
        for transaction in transactions:
            customer_data[transaction.customer_id]['spending'] += transaction.amount
            customer_data[transaction.customer_id]['transactions'] += 1
        
        chart_data = []
        for customer in customers[:20]:  # Top 20 customers
            data = customer_data.get(customer.customer_id, {'spending': Decimal('0'), 'transactions': 0})
            chart_data.append({
                'name': customer.name,
                'spending': float(data['spending']),
                'transactions': data['transactions']
            })
        
        # Sort by spending
        chart_data = sorted(chart_data, key=lambda x: x['spending'], reverse=True)
        
        return JsonResponse({'data': chart_data})
    
    return JsonResponse({'error': 'Invalid data type'})

# Class-based view for admin integration
@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get generated data
        customers = AnalyticsDataManager.get_customers()
        transactions = AnalyticsDataManager.get_transactions()
        merchants = AnalyticsDataManager.get_merchants()
        
        # Add analytics data to context
        context.update({
            'total_customers': len(customers),
            'total_transactions': len(transactions),
            'total_revenue': sum([t.amount for t in transactions]),
            'customers': customers[:20],
            'merchants': merchants[:10],
        })
        
        return context