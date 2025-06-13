from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import connection
from django.conf import settings
import time
import logging

logger = logging.getLogger('phantom_apps')

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
