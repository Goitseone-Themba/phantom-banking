<<<<<<< Updated upstream
=======
"""
Custom exception handling for Phantom Banking
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('phantom_apps')

def custom_exception_handler(exc, context):
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

# Custom Error Codes
class PhantomBankingErrorCodes:
    CUSTOMER_NOT_FOUND = 'CUSTOMER_NOT_FOUND'
    CUSTOMER_NOT_OWNED_BY_MERCHANT = 'CUSTOMER_NOT_OWNED_BY_MERCHANT'
    WALLET_NOT_FOUND = 'WALLET_NOT_FOUND'
    WALLET_CREATION_FAILED = 'WALLET_CREATION_FAILED'
    MERCHANT_NOT_FOUND = 'MERCHANT_NOT_FOUND'
    MERCHANT_HAS_NO_WALLETS = 'MERCHANT_HAS_NO_WALLETS'
    INVALID_CUSTOMER_DATA = 'INVALID_CUSTOMER_DATA'
    INVALID_MERCHANT_DATA = 'INVALID_MERCHANT_DATA'
    DATABASE_ERROR = 'DATABASE_ERROR'
    PERMISSION_DENIED = 'PERMISSION_DENIED'

def custom_exception_handler(exc, context):
    """Custom exception handler for better error responses"""
    response = exception_handler(exc, context)
    
    if response is not None:
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
    def __init__(self, message, error_code=None, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class CustomerNotFoundError(PhantomBankingException):
    """Exception for customer not found"""
    def __init__(self, customer_id):
        message = f"Customer with ID {customer_id} not found"
        super().__init__(
            message=message,
            error_code=PhantomBankingErrorCodes.CUSTOMER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND
        )

class CustomerNotOwnedError(PhantomBankingException):
    """Exception for customer not owned by merchant"""
    def __init__(self, customer_id, merchant_id):
        message = f"Customer {customer_id} is not owned by merchant {merchant_id}"
        super().__init__(
            message=message,
            error_code=PhantomBankingErrorCodes.CUSTOMER_NOT_OWNED_BY_MERCHANT,
            status_code=status.HTTP_403_FORBIDDEN
        )
class WalletNotFoundError(PhantomBankingException):
    """Exception for wallet not found"""
    def __init__(self, customer_id=None, wallet_id=None):
        if customer_id:
            message = f"No wallet found for customer {customer_id}"
        elif wallet_id:
            message = f"Wallet with ID {wallet_id} not found"
        else:
            message = "Wallet not found"
        super().__init__(
            message=message,
            error_code=PhantomBankingErrorCodes.WALLET_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND
        )

class MerchantHasNoWalletsError(PhantomBankingException):
    """Exception for merchant with no wallets"""
    def __init__(self, merchant_id):
        message = f"Merchant {merchant_id} has no wallets"
        super().__init__(
            message=message,
            error_code=PhantomBankingErrorCodes.MERCHANT_HAS_NO_WALLETS,
            status_code=status.HTTP_404_NOT_FOUND
        )
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


>>>>>>> Stashed changes
