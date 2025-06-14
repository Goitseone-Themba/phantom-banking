from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout
import logging

logger = logging.getLogger(__name__)

class UUIDValidationErrorMiddleware:
    """
    Middleware to handle UUID validation errors in user sessions.
    
    This occurs when the User model uses UUID primary keys but there are
    old sessions with integer user IDs.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except ValidationError as e:
            # Check if this is a UUID validation error
            if 'is not a valid UUID' in str(e):
                logger.warning(f"UUID validation error for session {request.session.session_key}: {e}")
                
                # Clear the problematic session
                request.session.flush()
                
                # If this was an admin request, redirect to login
                if request.path.startswith('/admin/'):
                    return HttpResponseRedirect('/admin/login/?next=' + request.path)
                
                # For API requests, let it continue without a session
                if request.path.startswith('/api/'):
                    response = self.get_response(request)
                else:
                    # For other requests, redirect to home
                    return HttpResponseRedirect('/')
            else:
                # Re-raise if it's not a UUID validation error
                raise
        
        return response

