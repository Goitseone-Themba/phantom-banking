import time
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.contrib.sessions.models import Session
from .metrics import (
    app_requests_total, app_request_duration, app_active_sessions,
    db_query_duration, db_query_counter, errors_total,
    response_time_p95, throughput
)


class PrometheusMetricsMiddleware(MiddlewareMixin):
    """Middleware to collect HTTP request metrics"""
    
    def process_request(self, request):
        """Start timing the request"""
        request._prometheus_start_time = time.time()
        request._prometheus_db_queries_start = len(connection.queries)
        
        # Count active sessions
        try:
            active_sessions = Session.objects.filter(
                expire_date__gt=time.time()
            ).count()
            app_active_sessions.set(active_sessions)
        except Exception:
            pass
        
        return None
    
    def process_response(self, request, response):
        """Record metrics after processing response"""
        if hasattr(request, '_prometheus_start_time'):
            # Calculate request duration
            duration = time.time() - request._prometheus_start_time
            app_request_duration.observe(duration)
            
            # Count HTTP requests by method, endpoint, and status
            method = request.method
            path = self._get_path_pattern(request)
            status = str(response.status_code)
            
            app_requests_total.labels(
                method=method,
                endpoint=path,
                status=status
            ).inc()
            
            # Track database queries
            if hasattr(request, '_prometheus_db_queries_start'):
                db_queries = len(connection.queries) - request._prometheus_db_queries_start
                if db_queries > 0:
                    avg_query_time = sum(
                        float(query['time']) for query in connection.queries[-db_queries:]
                    ) / db_queries
                    
                    db_query_duration.observe(avg_query_time)
                    db_query_counter.labels(operation='select').inc(db_queries)
        
        return response
    
    def process_exception(self, request, exception):
        """Track exceptions and errors"""
        error_type = exception.__class__.__name__
        errors_total.labels(type=error_type, severity='error').inc()
        return None
    
    def _get_path_pattern(self, request):
        """Extract URL pattern for grouping similar endpoints"""
        path = request.path
        
        # Replace UUIDs with placeholder
        import re
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/',
            '/<uuid>/',
            path
        )
        
        # Replace numeric IDs with placeholder
        path = re.sub(r'/\d+/', '/<id>/', path)
        
        return path


class DatabaseMetricsMiddleware(MiddlewareMixin):
    """Middleware specifically for database performance tracking"""
    
    def process_request(self, request):
        """Reset query tracking"""
        connection.queries_log.clear() if hasattr(connection, 'queries_log') else None
        return None
    
    def process_response(self, request, response):
        """Log database query metrics"""
        for query in connection.queries:
            operation = self._extract_operation(query['sql'])
            db_query_counter.labels(operation=operation).inc()
            db_query_duration.observe(float(query['time']))
        
        return response
    
    def _extract_operation(self, sql):
        """Extract SQL operation type from query"""
        sql_upper = sql.upper().strip()
        if sql_upper.startswith('SELECT'):
            return 'select'
        elif sql_upper.startswith('INSERT'):
            return 'insert'
        elif sql_upper.startswith('UPDATE'):
            return 'update'
        elif sql_upper.startswith('DELETE'):
            return 'delete'
        else:
            return 'other'

