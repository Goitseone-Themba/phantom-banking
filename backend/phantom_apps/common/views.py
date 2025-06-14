from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from django.urls import reverse
from django.conf import settings
import time
import logging

logger = logging.getLogger('phantom_apps')


class APIRootView(APIView):
    """API v1 root endpoint with available services information"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return information about available API endpoints"""
        try:
            base_url = request.build_absolute_uri('/api/v1/')
            
            return Response({
                'api': 'Phantom Banking API v1',
                'version': '1.0.0',
                'description': 'Embedded Accounts for the Unbanked - FNB Hackathon 2025',
                'documentation': request.build_absolute_uri('/api/docs/'),
                'status': 'operational',
                'endpoints': {
                    'authentication': {
                        'url': f"{base_url}auth/",
                        'description': 'User authentication and JWT token management'
                    },
                    'merchants': {
                        'url': f"{base_url}merchants/", 
                        'description': 'Merchant management, registration, and API credentials'
                    },
                    'customers': {
                        'url': f"{base_url}customers/",
                        'description': 'Customer profiles and account management'
                    },
                    'wallets': {
                        'url': f"{base_url}wallets/",
                        'description': 'Digital wallet operations and balance management'
                    },
                    'transactions': {
                        'url': f"{base_url}transactions/",
                        'description': 'Payment processing, QR codes, and EFT transactions'
                    },
                    'health': {
                        'url': f"{base_url}health/",
                        'description': 'API health monitoring and system status'
                    }
                },
                'mock_systems': {
                    'description': 'Development and testing endpoints',
                    'fnb': f"{base_url}mock-fnb/",
                    'mobile_money': f"{base_url}mock-mobile-money/"
                },
                'features': [
                    'JWT Authentication',
                    'QR Code Payments', 
                    'EFT Transactions',
                    'Multi-merchant Support',
                    'Real-time Transaction Processing',
                    'API Documentation',
                    'Comprehensive Health Monitoring'
                ]
            })
        except Exception as e:
            logger.error(f"API root view error: {e}")
            return Response({
                'error': 'Unable to generate API information',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheckView(APIView):
    """Basic health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'phantom-banking-api',
            'version': '1.0.0',
            'timestamp': time.time()
        })

class DatabaseHealthView(APIView):
    """Database connectivity check"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 as health_check")
                result = cursor.fetchone()
            
            connection_time = time.time() - start_time
            
            return Response({
                'database': {
                    'status': 'healthy',
                    'connection_time_ms': round(connection_time * 1000, 2),
                    'engine': settings.DATABASES['default']['ENGINE'],
                }
            })
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return Response({
                'database': {
                    'status': 'unhealthy',
                    'error': str(e)
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
