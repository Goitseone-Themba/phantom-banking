from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def div(value, divisor):
    """
    Divides the value by the divisor.
    Returns 0 if division by zero or invalid operation.
    """
    try:
        if divisor == 0:
            return 0
        return float(value) / float(divisor)
    except (ValueError, TypeError, InvalidOperation, ZeroDivisionError):
        return 0

@register.filter
def mul(value, multiplier):
    """
    Multiplies the value by the multiplier.
    Returns 0 if invalid operation.
    """
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError, InvalidOperation):
        return 0

