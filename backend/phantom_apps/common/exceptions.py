from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('phantom_apps')

def custom_exception_handler(exc, context):
    """
    Custom exception handler for better error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the exception
        logger.error(f"API Exception: {exc} - Context: {context}")
        
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code,
            'details': response.data if isinstance(response.data, dict) else {}
        }
        
        response.data = custom_response_data
    
    return response

class PhantomBankingException(Exception):
    """Base exception for Phantom Banking operations"""
    pass

class WalletException(PhantomBankingException):
    """Exception for wallet-related operations"""
    pass

class TransactionException(PhantomBankingException):
    """Exception for transaction-related operations"""
    pass

class PaymentChannelException(PhantomBankingException):
    """Exception for payment channel operations"""
    pass
