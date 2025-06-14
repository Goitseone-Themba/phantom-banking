from rest_framework import serializers
from datetime import datetime
from decimal import Decimal

class CustomerAnalyticsSerializer(serializers.Serializer):
    """Serializer for customer analytics data"""
    customer_id = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15, required=False)
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    risk_score = serializers.IntegerField(min_value=0, max_value=100)
    created_at = serializers.DateTimeField()
    
class TransactionAnalyticsSerializer(serializers.Serializer):
    """Serializer for transaction analytics data"""
    transaction_id = serializers.UUIDField()
    customer_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    merchant = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=50)
    transaction_date = serializers.DateTimeField()

class MerchantAnalyticsSerializer(serializers.Serializer):
    """Serializer for merchant analytics data"""
    merchant_id = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=50)
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()

class MonthlyRevenueSerializer(serializers.Serializer):
    """Serializer for monthly revenue data"""
    month = serializers.CharField(max_length=7)  # Format: YYYY-MM
    revenue = serializers.DecimalField(max_digits=15, decimal_places=2)

class CategoryBreakdownSerializer(serializers.Serializer):
    """Serializer for category breakdown data"""
    category = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)

class CustomerInsightSerializer(serializers.Serializer):
    """Serializer for customer insights"""
    insight_type = serializers.CharField(max_length=20)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500)
    value = serializers.CharField(max_length=50, required=False)

class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data"""
    total_customers = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_transaction_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    high_risk_customers = serializers.IntegerField()
    medium_risk_customers = serializers.IntegerField()
    low_risk_customers = serializers.IntegerField()

class CustomerDetailSerializer(serializers.Serializer):
    """Serializer for detailed customer analytics"""
    customer = CustomerAnalyticsSerializer()
    total_spent = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
    avg_transaction = serializers.DecimalField(max_digits=15, decimal_places=2)
    risk_level = serializers.CharField(max_length=10)
    monthly_spending = MonthlyRevenueSerializer(many=True)
    category_breakdown = CategoryBreakdownSerializer(many=True)
    insights = CustomerInsightSerializer(many=True)

class RiskAnalysisSerializer(serializers.Serializer):
    """Serializer for risk analysis data"""
    low_risk_count = serializers.IntegerField()
    medium_risk_count = serializers.IntegerField()
    high_risk_count = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    low_risk_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    medium_risk_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    high_risk_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

class ExportDataSerializer(serializers.Serializer):
    """Serializer for data export"""
    export_type = serializers.CharField(max_length=20)
    format = serializers.CharField(max_length=10, default='json')
    date_range = serializers.CharField(max_length=50, required=False)
    filters = serializers.JSONField(required=False)

class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data responses"""
    chart_type = serializers.CharField(max_length=20)
    data = serializers.JSONField()
    metadata = serializers.JSONField(required=False)

# Custom validation functions
def validate_risk_score(value):
    """Validate risk score is within acceptable range"""
    if value < 0 or value > 100:
        raise serializers.ValidationError("Risk score must be between 0 and 100")
    return value

def validate_positive_amount(value):
    """Validate amount is positive"""
    if value <= 0:
        raise serializers.ValidationError("Amount must be positive")
    return value

def validate_date_range(start_date, end_date):
    """Validate date range"""
    if start_date > end_date:
        raise serializers.ValidationError("Start date must be before end date")
    return True

# API Response Serializers
class SuccessResponseSerializer(serializers.Serializer):
    """Standard success response"""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(max_length=200)
    data = serializers.JSONField(required=False)

class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField(max_length=200)
    details = serializers.JSONField(required=False)