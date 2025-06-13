import time
import psutil
from django.conf import settings
from django.db import connections
from django.core.cache import cache
from prometheus_client import Counter, Histogram, Gauge, Info

# System metrics
system_info = Info('phantom_banking_system_info', 'System information')
system_cpu_usage = Gauge('phantom_banking_cpu_usage_percent', 'CPU usage percentage')
system_memory_usage = Gauge('phantom_banking_memory_usage_bytes', 'Memory usage in bytes')
system_disk_usage = Gauge('phantom_banking_disk_usage_percent', 'Disk usage percentage')
system_network_io = Gauge('phantom_banking_network_io_bytes_total', 'Network I/O bytes', ['direction'])

# Database metrics
db_connections_active = Gauge('phantom_banking_db_connections_active', 'Active database connections')
db_query_duration = Histogram('phantom_banking_db_query_duration_seconds', 'Database query duration')
db_query_counter = Counter('phantom_banking_db_queries_total', 'Total database queries', ['operation'])

# Application metrics
app_requests_total = Counter('phantom_banking_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
app_request_duration = Histogram('phantom_banking_request_duration_seconds', 'HTTP request duration')
app_active_sessions = Gauge('phantom_banking_active_sessions', 'Number of active user sessions')

# Business metrics - Customers
customers_total = Gauge('phantom_banking_customers_total', 'Total number of customers')
customers_verified = Gauge('phantom_banking_customers_verified', 'Number of verified customers')
customers_created_today = Gauge('phantom_banking_customers_created_today', 'Customers created today')

# Business metrics - Merchants
merchants_total = Gauge('phantom_banking_merchants_total', 'Total number of merchants')
merchants_active = Gauge('phantom_banking_merchants_active', 'Number of active merchants')
merchants_api_calls = Counter('phantom_banking_merchant_api_calls_total', 'Total merchant API calls', ['merchant_id', 'endpoint'])

# Business metrics - Wallets
wallets_total = Gauge('phantom_banking_wallets_total', 'Total number of wallets')
wallets_balance_total = Gauge('phantom_banking_wallets_balance_total', 'Total wallet balance in BWP')
wallets_frozen = Gauge('phantom_banking_wallets_frozen', 'Number of frozen wallets')
wallets_kyc_verified = Gauge('phantom_banking_wallets_kyc_verified', 'Number of KYC verified wallets')

# Business metrics - Transactions
transactions_total = Counter('phantom_banking_transactions_total', 'Total transactions', ['type', 'status'])
transactions_amount = Histogram('phantom_banking_transaction_amount_bwp', 'Transaction amounts in BWP', ['type'])
transactions_duration = Histogram('phantom_banking_transaction_duration_seconds', 'Transaction processing time')
transactions_failed = Counter('phantom_banking_transactions_failed_total', 'Failed transactions', ['reason'])

# Business metrics - QR Codes
qr_codes_generated = Counter('phantom_banking_qr_codes_generated_total', 'Total QR codes generated')
qr_codes_scanned = Counter('phantom_banking_qr_codes_scanned_total', 'Total QR codes scanned')
qr_codes_expired = Counter('phantom_banking_qr_codes_expired_total', 'Total expired QR codes')
qr_codes_active = Gauge('phantom_banking_qr_codes_active', 'Currently active QR codes')

# Business metrics - KYC
kyc_verifications_total = Counter('phantom_banking_kyc_verifications_total', 'Total KYC verifications', ['status'])
kyc_pending = Gauge('phantom_banking_kyc_pending', 'Pending KYC verifications')
kyc_processing_duration = Histogram('phantom_banking_kyc_processing_duration_seconds', 'KYC processing time')

# Business metrics - EFT Payments
eft_payments_total = Counter('phantom_banking_eft_payments_total', 'Total EFT payments', ['bank', 'status'])
eft_payment_amount = Histogram('phantom_banking_eft_payment_amount_bwp', 'EFT payment amounts in BWP', ['bank'])
eft_processing_duration = Histogram('phantom_banking_eft_processing_duration_seconds', 'EFT processing time', ['bank'])

# Security metrics
security_failed_logins = Counter('phantom_banking_failed_logins_total', 'Failed login attempts', ['ip_address'])
security_suspicious_activity = Counter('phantom_banking_suspicious_activity_total', 'Suspicious activity detected', ['type'])
security_api_rate_limits = Counter('phantom_banking_api_rate_limits_hit_total', 'API rate limits hit', ['endpoint'])

# Cache metrics
cache_hits = Counter('phantom_banking_cache_hits_total', 'Cache hits')
cache_misses = Counter('phantom_banking_cache_misses_total', 'Cache misses')
cache_operations = Histogram('phantom_banking_cache_operation_duration_seconds', 'Cache operation duration', ['operation'])

# Error metrics
errors_total = Counter('phantom_banking_errors_total', 'Total application errors', ['type', 'severity'])
error_rate = Gauge('phantom_banking_error_rate_percent', 'Error rate percentage')

# Performance metrics
response_time_p95 = Gauge('phantom_banking_response_time_p95_seconds', 'Response time 95th percentile')
throughput = Gauge('phantom_banking_throughput_requests_per_second', 'Requests per second')


def collect_system_metrics():
    """Collect system-level metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.used)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        system_disk_usage.set(disk.percent)
        
        # Network I/O
        network_io = psutil.net_io_counters()
        system_network_io.labels(direction='sent').set(network_io.bytes_sent)
        system_network_io.labels(direction='received').set(network_io.bytes_recv)
        
        # System info
        system_info.info({
            'version': getattr(settings, 'PHANTOM_BANKING_VERSION', '1.0.0'),
            'environment': 'development' if settings.DEBUG else 'production',
            'python_version': f"{psutil.version_info.major}.{psutil.version_info.minor}"
        })
        
    except Exception as e:
        errors_total.labels(type='system_metrics', severity='warning').inc()


def collect_database_metrics():
    """Collect database-related metrics"""
    try:
        from django.db import connection
        
        # Database connections
        db_connections_active.set(len(connections.all()))
        
        # Query performance (this would need custom middleware to track)
        # db_query_duration and db_query_counter are updated in middleware
        
    except Exception as e:
        errors_total.labels(type='database_metrics', severity='warning').inc()


def collect_business_metrics():
    """Collect business-specific metrics"""
    try:
        from django.utils import timezone
        from phantom_apps.customers.models import Customer
        from phantom_apps.merchants.models import Merchant
        from phantom_apps.wallets.models import Wallet
        from phantom_apps.transactions.models import Transaction, QRCode, EFTPayment
        from phantom_apps.kyc.models import KYCRecord
        
        # Customer metrics
        customers_total.set(Customer.objects.count())
        customers_verified.set(Customer.objects.filter(is_verified=True).count())
        
        today = timezone.now().date()
        customers_created_today.set(
            Customer.objects.filter(created_at__date=today).count()
        )
        
        # Merchant metrics
        merchants_total.set(Merchant.objects.count())
        merchants_active.set(Merchant.objects.filter(is_active=True).count())
        
        # Wallet metrics
        wallets_total.set(Wallet.objects.count())
        wallets_frozen.set(Wallet.objects.filter(is_frozen=True).count())
        wallets_kyc_verified.set(Wallet.objects.filter(is_kyc_verified=True).count())
        
        # Calculate total wallet balance
        from django.db.models import Sum
        total_balance = Wallet.objects.aggregate(total=Sum('balance'))['total'] or 0
        wallets_balance_total.set(float(total_balance))
        
        # QR Code metrics
        qr_codes_active.set(
            QRCode.objects.filter(
                status='active',
                expires_at__gt=timezone.now()
            ).count()
        )
        
        # KYC metrics
        kyc_pending.set(
            KYCRecord.objects.filter(status='pending').count()
        )
        
    except Exception as e:
        errors_total.labels(type='business_metrics', severity='warning').inc()


def collect_cache_metrics():
    """Collect cache-related metrics"""
    try:
        from django.core.cache import cache
        
        # Test cache connectivity
        start_time = time.time()
        cache.set('health_check', 'ok', 30)
        result = cache.get('health_check')
        duration = time.time() - start_time
        
        cache_operations.labels(operation='health_check').observe(duration)
        
        if result == 'ok':
            cache_hits.inc()
        else:
            cache_misses.inc()
            
    except Exception as e:
        errors_total.labels(type='cache_metrics', severity='warning').inc()


def collect_all_metrics():
    """Collect all metrics - called by monitoring endpoint"""
    collect_system_metrics()
    collect_database_metrics()
    collect_business_metrics()
    collect_cache_metrics()

