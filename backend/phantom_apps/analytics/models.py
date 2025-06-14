# phantom_apps/analytics/models.py

from django.db import models
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
import random

class MockCustomer:
    """Mock customer data for analytics - no database required"""
    
    def __init__(self, customer_id, name, email, phone, total_balance, risk_score):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.total_balance = total_balance
        self.risk_score = risk_score
        self.created_at = datetime.now() - timedelta(days=random.randint(30, 365))

class MockTransaction:
    """Mock transaction data for analytics"""
    
    def __init__(self, transaction_id, customer_id, amount, merchant, category, date):
        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.amount = amount
        self.merchant = merchant
        self.category = category
        self.transaction_date = date

class MockMerchant:
    """Mock merchant data for analytics"""
    
    def __init__(self, merchant_id, name, category, total_revenue, transaction_count):
        self.merchant_id = merchant_id
        self.name = name
        self.category = category
        self.total_revenue = total_revenue
        self.transaction_count = transaction_count

class AnalyticsDataGenerator:
    """Generate mock data for analytics dashboard"""
    
    @staticmethod
    def generate_customers(count=100):
        """Generate mock customer data"""
        customers = []
        
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa', 'Mark', 'Anna',
                      'Robert', 'Emily', 'James', 'Maria', 'William', 'Jessica', 'Richard', 'Ashley']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            customer = MockCustomer(
                customer_id=str(uuid.uuid4()),
                name=f"{first_name} {last_name}",
                email=f"{first_name.lower()}.{last_name.lower()}@email.com",
                phone=f"555-{random.randint(1000, 9999)}",
                total_balance=Decimal(random.randint(1000, 100000)),
                risk_score=random.randint(1, 100)
            )
            customers.append(customer)
        
        return customers
    
    @staticmethod
    def generate_transactions(customers, count=1000):
        """Generate mock transaction data"""
        transactions = []
        
        merchants = [
            'Amazon', 'Walmart', 'Target', 'Starbucks', 'McDonald\'s', 'Shell Gas', 'CVS Pharmacy',
            'Home Depot', 'Best Buy', 'Costco', 'Uber', 'Netflix', 'Spotify', 'Apple Store',
            'Google Play', 'Steam', 'PayPal', 'Venmo', 'Cash App', 'Zelle'
        ]
        
        categories = [
            'groceries', 'restaurants', 'gas', 'shopping', 'entertainment', 
            'utilities', 'healthcare', 'education', 'travel', 'other'
        ]
        
        for i in range(count):
            customer = random.choice(customers)
            
            transaction = MockTransaction(
                transaction_id=str(uuid.uuid4()),
                customer_id=customer.customer_id,
                amount=Decimal(random.randint(10, 500)),
                merchant=random.choice(merchants),
                category=random.choice(categories),
                date=datetime.now() - timedelta(days=random.randint(0, 365))
            )
            transactions.append(transaction)
        
        return transactions
    
    @staticmethod
    def generate_merchants(count=50):
        """Generate mock merchant data"""
        merchants = []
        
        merchant_names = [
            'Amazon Store', 'Walmart Supercenter', 'Target Corporation', 'Starbucks Coffee',
            'McDonald\'s Restaurant', 'Shell Gas Station', 'CVS Pharmacy', 'Home Depot',
            'Best Buy Electronics', 'Costco Wholesale', 'Uber Technologies', 'Netflix Inc',
            'Spotify Music', 'Apple Store', 'Google Play Store', 'Steam Gaming',
            'PayPal Holdings', 'Venmo Payment', 'Cash App Square', 'Zelle Network'
        ]
        
        categories = ['retail', 'food', 'gas', 'pharmacy', 'entertainment', 'technology', 'finance']
        
        for i in range(count):
            if i < len(merchant_names):
                name = merchant_names[i]
            else:
                name = f"Merchant {i+1}"
            
            merchant = MockMerchant(
                merchant_id=str(uuid.uuid4()),
                name=name,
                category=random.choice(categories),
                total_revenue=Decimal(random.randint(10000, 1000000)),
                transaction_count=random.randint(100, 5000)
            )
            merchants.append(merchant)
        
        return merchants