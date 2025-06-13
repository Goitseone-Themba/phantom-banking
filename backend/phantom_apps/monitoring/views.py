from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .metrics import collect_all_metrics
import json


@never_cache
@csrf_exempt
def metrics_view(request):
    """Prometheus metrics endpoint"""
    # Collect all metrics before generating output
    collect_all_metrics()
    
    # Generate Prometheus formatted metrics
    metrics_data = generate_latest()
    return HttpResponse(metrics_data, content_type=CONTENT_TYPE_LATEST)


@method_decorator(staff_member_required, name='dispatch')
class HealthCheckView(View):
    """Health check endpoint for monitoring"""
    
    def get(self, request):
        """Return system health status"""
        from django.db import connection
        from django.core.cache import cache
        import time
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }
        
        # Database health check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status['checks']['database'] = {'status': 'healthy'}
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        # Cache health check
        try:
            cache.set('health_check', 'ok', 30)
            result = cache.get('health_check')
            if result == 'ok':
                health_status['checks']['cache'] = {'status': 'healthy'}
            else:
                raise Exception("Cache test failed")
        except Exception as e:
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return JsonResponse(health_status, status=status_code)


@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(View):
    """Admin dashboard with monitoring overview"""
    
    def get(self, request):
        """Render admin dashboard"""
        from django.utils import timezone
        from phantom_apps.customers.models import Customer
        from phantom_apps.merchants.models import Merchant
        from phantom_apps.wallets.models import Wallet
        from phantom_apps.transactions.models import Transaction, QRCode
        from phantom_apps.kyc.models import KYCRecord
        from django.db.models import Sum, Count, Avg
        import psutil
        import time
        
        # Get system metrics with proper error handling
        try:
            # Get CPU usage over 1 second interval for more accurate reading
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_stats = {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'disk_percent': round(disk.percent, 1),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'cpu_count': psutil.cpu_count(),
                'uptime': time.time() - psutil.boot_time(),
            }
        except Exception as e:
            # Fallback system stats if psutil fails
            system_stats = {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'memory_used_gb': 0,
                'memory_total_gb': 0,
                'disk_used_gb': 0,
                'disk_total_gb': 0,
                'cpu_count': 1,
                'uptime': 0,
                'error': str(e)
            }
        
        # Business metrics
        today = timezone.now().date()
        
        customer_stats = {
            'total': Customer.objects.count(),
            'verified': Customer.objects.filter(is_verified=True).count(),
            'created_today': Customer.objects.filter(created_at__date=today).count(),
        }
        
        merchant_stats = {
            'total': Merchant.objects.count(),
            'active': Merchant.objects.filter(is_active=True).count(),
        }
        
        wallet_stats = {
            'total': Wallet.objects.count(),
            'total_balance': float(Wallet.objects.aggregate(total=Sum('balance'))['total'] or 0),
            'frozen': Wallet.objects.filter(is_frozen=True).count(),
            'kyc_verified': Wallet.objects.filter(is_kyc_verified=True).count(),
        }
        
        transaction_stats = {
            'total': Transaction.objects.count(),
            'today': Transaction.objects.filter(created_at__date=today).count(),
            'total_volume': float(Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0),
            'avg_amount': float(Transaction.objects.aggregate(avg=Avg('amount'))['avg'] or 0),
        }
        
        qr_stats = {
            'total': QRCode.objects.count(),
            'active': QRCode.objects.filter(
                status='active',
                expires_at__gt=timezone.now()
            ).count(),
        }
        
        kyc_stats = {
            'total': KYCRecord.objects.count(),
            'pending': KYCRecord.objects.filter(status='pending').count(),
            'approved': KYCRecord.objects.filter(status='approved').count(),
            'rejected': KYCRecord.objects.filter(status='rejected').count(),
        }
        
        # Get recent businesses for initial table data
        recent_merchants = Merchant.objects.select_related('user').order_by('-created_at')[:5]
        
        merchants_data = []
        for merchant in recent_merchants:
            # Get wallet count and total balance for this merchant
            merchant_wallets = Wallet.objects.filter(merchant=merchant)
            wallet_count = merchant_wallets.count()
            total_balance = merchant_wallets.aggregate(total=Sum('balance'))['total'] or 0
            
            merchants_data.append({
                'id': str(merchant.id),
                'name': merchant.business_name,
                'industry': merchant.get_business_type_display() if hasattr(merchant, 'get_business_type_display') else 'Other',
                'wallets': wallet_count,
                'total_value': float(total_balance),
                'status': 'active' if merchant.is_active else 'inactive',
                'created_at': merchant.created_at.isoformat()
            })
        
        # Convert stats to JSON-safe format for JavaScript
        context = {
            'system_stats': json.dumps(system_stats),
            'customer_stats': json.dumps(customer_stats),
            'merchant_stats': json.dumps(merchant_stats),
            'wallet_stats': json.dumps(wallet_stats),
            'transaction_stats': json.dumps(transaction_stats),
            'qr_stats': json.dumps(qr_stats),
            'kyc_stats': json.dumps(kyc_stats),
            'recent_merchants': json.dumps(merchants_data),
        }
        
        return render(request, 'admin/monitoring/dashboard.html', context)


@method_decorator(staff_member_required, name='dispatch')
class DashboardDataView(View):
    """API endpoint for dashboard data updates"""
    
    def get(self, request):
        """Return dashboard data as JSON for AJAX updates"""
        from django.utils import timezone
        from phantom_apps.customers.models import Customer
        from phantom_apps.merchants.models import Merchant
        from phantom_apps.wallets.models import Wallet
        from phantom_apps.transactions.models import Transaction, QRCode
        from phantom_apps.kyc.models import KYCRecord
        from django.db.models import Sum, Count, Avg
        import psutil
        import time
        
        # Get system metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_stats = {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'disk_percent': round(disk.percent, 1),
                'timestamp': time.time()
            }
        except Exception:
            system_stats = {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'timestamp': time.time()
            }
        
        # Business metrics
        today = timezone.now().date()
        
        customer_stats = {
            'total': Customer.objects.count(),
            'verified': Customer.objects.filter(is_verified=True).count(),
            'created_today': Customer.objects.filter(created_at__date=today).count(),
        }
        
        merchant_stats = {
            'total': Merchant.objects.count(),
            'active': Merchant.objects.filter(is_active=True).count(),
        }
        
        wallet_stats = {
            'total': Wallet.objects.count(),
            'total_balance': float(Wallet.objects.aggregate(total=Sum('balance'))['total'] or 0),
            'frozen': Wallet.objects.filter(is_frozen=True).count(),
            'kyc_verified': Wallet.objects.filter(is_kyc_verified=True).count(),
        }
        
        transaction_stats = {
            'total': Transaction.objects.count(),
            'today': Transaction.objects.filter(created_at__date=today).count(),
            'total_volume': float(Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0),
            'avg_amount': float(Transaction.objects.aggregate(avg=Avg('amount'))['avg'] or 0),
        }
        
        qr_stats = {
            'total': QRCode.objects.count(),
            'active': QRCode.objects.filter(
                status='active',
                expires_at__gt=timezone.now()
            ).count(),
        }
        
        kyc_stats = {
            'total': KYCRecord.objects.count(),
            'pending': KYCRecord.objects.filter(status='pending').count(),
            'approved': KYCRecord.objects.filter(status='approved').count(),
            'rejected': KYCRecord.objects.filter(status='rejected').count(),
        }
        
        # Get recent businesses for table
        recent_merchants = Merchant.objects.select_related('user').order_by('-created_at')[:5]
        
        merchants_data = []
        for merchant in recent_merchants:
            # Get wallet count and total balance for this merchant
            merchant_wallets = Wallet.objects.filter(merchant=merchant)
            wallet_count = merchant_wallets.count()
            total_balance = merchant_wallets.aggregate(total=Sum('balance'))['total'] or 0
            
            merchants_data.append({
                'id': str(merchant.id),
                'name': merchant.business_name,
                'industry': merchant.get_business_type_display() if hasattr(merchant, 'get_business_type_display') else 'Other',
                'wallets': wallet_count,
                'total_value': float(total_balance),
                'status': 'active' if merchant.is_active else 'inactive',
                'created_at': merchant.created_at.isoformat()
            })
        
        data = {
            'system_stats': system_stats,
            'customer_stats': customer_stats,
            'merchant_stats': merchant_stats,
            'wallet_stats': wallet_stats,
            'transaction_stats': transaction_stats,
            'qr_stats': qr_stats,
            'kyc_stats': kyc_stats,
            'recent_merchants': merchants_data,
        }
        
        return JsonResponse(data)