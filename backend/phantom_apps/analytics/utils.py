# phantom_apps/analytics/utils.py

from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
import json
import random

class AnalyticsHelper:
    """Helper functions for analytics calculations"""
    
    @staticmethod
    def calculate_monthly_trend(transactions, months=12):
        """Calculate monthly spending trend"""
        monthly_data = defaultdict(Decimal)
        
        for transaction in transactions:
            month_key = transaction.transaction_date.strftime('%Y-%m')
            monthly_data[month_key] += transaction.amount
        
        # Get last N months
        sorted_months = sorted(monthly_data.keys())[-months:]
        return [{'month': month, 'amount': float(monthly_data[month])} for month in sorted_months]
    
    @staticmethod
    def calculate_category_breakdown(transactions):
        """Calculate spending by category"""
        category_data = defaultdict(Decimal)
        
        for transaction in transactions:
            category_data[transaction.category] += transaction.amount
        
        return [{'category': k, 'amount': float(v)} for k, v in category_data.items()]
    
    @staticmethod
    def calculate_risk_score(customer, transactions):
        """Calculate customer risk score based on spending patterns"""
        if not transactions:
            return 50  # Default medium risk
        
        # Factors for risk calculation
        total_spent = sum([t.amount for t in transactions])
        transaction_count = len(transactions)
        avg_transaction = total_spent / transaction_count if transaction_count > 0 else 0
        
        # High-risk indicators
        risk_score = 30  # Base score
        
        # High spending
        if total_spent > Decimal('10000'):
            risk_score += 20
        
        # High frequency
        if transaction_count > 100:
            risk_score += 15
        
        # High average transaction
        if avg_transaction > Decimal('500'):
            risk_score += 15
        
        # Random factors for demo
        risk_score += random.randint(-10, 20)
        
        return max(0, min(100, risk_score))
    
    @staticmethod
    def get_spending_insights(customer, transactions):
        """Get spending insights for a customer"""
        if not transactions:
            return []
        
        insights = []
        total_spent = sum([t.amount for t in transactions])
        transaction_count = len(transactions)
        avg_transaction = total_spent / transaction_count
        
        # Spending pattern insights
        if avg_transaction > Decimal('200'):
            insights.append({
                'type': 'info',
                'title': 'High-Value Transactions',
                'description': f'Customer averages ${avg_transaction:.2f} per transaction, indicating premium spending habits.'
            })
        
        if transaction_count > 50:
            insights.append({
                'type': 'warning',
                'title': 'High Transaction Frequency',
                'description': f'Customer has {transaction_count} transactions, showing high engagement.'
            })
        
        # Category insights
        category_spending = defaultdict(Decimal)
        for transaction in transactions:
            category_spending[transaction.category] += transaction.amount
        
        top_category = max(category_spending.items(), key=lambda x: x[1])
        insights.append({
            'type': 'success',
            'title': 'Top Spending Category',
            'description': f'Spends most in {top_category[0]} category (${top_category[1]:.2f}).'
        })
        
        return insights
    
    @staticmethod
    def export_customer_data(customer, transactions):
        """Export customer data to JSON format"""
        customer_spending = sum([t.amount for t in transactions])
        
        data = {
            'customer_info': {
                'id': customer.customer_id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'total_balance': float(customer.total_balance),
                'risk_score': customer.risk_score
            },
            'spending_summary': {
                'total_spent': float(customer_spending),
                'transaction_count': len(transactions),
                'average_transaction': float(customer_spending / len(transactions)) if transactions else 0,
                'monthly_breakdown': AnalyticsHelper.calculate_monthly_trend(transactions),
                'category_breakdown': AnalyticsHelper.calculate_category_breakdown(transactions)
            },
            'recent_transactions': [
                {
                    'id': t.transaction_id,
                    'amount': float(t.amount),
                    'merchant': t.merchant,
                    'category': t.category,
                    'date': t.transaction_date.isoformat()
                }
                for t in sorted(transactions, key=lambda x: x.transaction_date, reverse=True)[:10]
            ],
            'export_metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_records': len(transactions)
            }
        }
        
        return data

class ReportGenerator:
    """Generate various analytics reports"""
    
    @staticmethod
    def generate_customer_summary_report(customers, transactions):
        """Generate a summary report for all customers"""
        customer_stats = {}
        
        # Calculate stats for each customer
        for customer in customers:
            customer_transactions = [t for t in transactions if t.customer_id == customer.customer_id]
            total_spent = sum([t.amount for t in customer_transactions])
            
            customer_stats[customer.customer_id] = {
                'customer': customer,
                'total_spent': total_spent,
                'transaction_count': len(customer_transactions),
                'avg_transaction': total_spent / len(customer_transactions) if customer_transactions else 0,
                'risk_level': 'High' if customer.risk_score > 70 else 'Medium' if customer.risk_score > 30 else 'Low'
            }
        
        return customer_stats
    
    @staticmethod
    def generate_merchant_report(transactions):
        """Generate merchant performance report"""
        merchant_stats = defaultdict(lambda: {
            'revenue': Decimal('0'),
            'transaction_count': 0,
            'customers': set()
        })
        
        for transaction in transactions:
            merchant = transaction.merchant
            merchant_stats[merchant]['revenue'] += transaction.amount
            merchant_stats[merchant]['transaction_count'] += 1
            merchant_stats[merchant]['customers'].add(transaction.customer_id)
        
        # Convert to list format
        merchant_report = []
        for merchant, stats in merchant_stats.items():
            merchant_report.append({
                'merchant': merchant,
                'revenue': float(stats['revenue']),
                'transaction_count': stats['transaction_count'],
                'unique_customers': len(stats['customers']),
                'avg_transaction': float(stats['revenue'] / stats['transaction_count']) if stats['transaction_count'] > 0 else 0
            })
        
        return sorted(merchant_report, key=lambda x: x['revenue'], reverse=True)
    
    @staticmethod
    def generate_risk_analysis_report(customers):
        """Generate risk analysis report"""
        risk_buckets = {
            'low': [],
            'medium': [],
            'high': []
        }
        
        for customer in customers:
            if customer.risk_score < 30:
                risk_buckets['low'].append(customer)
            elif customer.risk_score < 70:
                risk_buckets['medium'].append(customer)
            else:
                risk_buckets['high'].append(customer)
        
        return {
            'summary': {
                'low_risk_count': len(risk_buckets['low']),
                'medium_risk_count': len(risk_buckets['medium']),
                'high_risk_count': len(risk_buckets['high']),
                'total_customers': len(customers)
            },
            'risk_distribution': {
                'low_risk_percentage': (len(risk_buckets['low']) / len(customers)) * 100 if customers else 0,
                'medium_risk_percentage': (len(risk_buckets['medium']) / len(customers)) * 100 if customers else 0,
                'high_risk_percentage': (len(risk_buckets['high']) / len(customers)) * 100 if customers else 0
            },
            'high_risk_customers': risk_buckets['high'][:10]  # Top 10 high-risk customers
        }

class DataValidationHelper:
    """Helper functions for data validation"""
    
    @staticmethod
    def validate_customer_data(customer_data):
        """Validate customer data structure"""
        required_fields = ['customer_id', 'name', 'email', 'total_balance', 'risk_score']
        
        for field in required_fields:
            if not hasattr(customer_data, field):
                return False, f"Missing required field: {field}"
        
        if customer_data.risk_score < 0 or customer_data.risk_score > 100:
            return False, "Risk score must be between 0 and 100"
        
        return True, "Valid"
    
    @staticmethod
    def validate_transaction_data(transaction_data):
        """Validate transaction data structure"""
        required_fields = ['transaction_id', 'customer_id', 'amount', 'merchant', 'category', 'transaction_date']
        
        for field in required_fields:
            if not hasattr(transaction_data, field):
                return False, f"Missing required field: {field}"
        
        if transaction_data.amount <= 0:
            return False, "Transaction amount must be positive"
        
        return True, "Valid"