"""
Global discount code system for the application.

This module provides functionality for managing and applying global discount codes
that can be used across the platform.
"""

from .enums import DiscountType, DiscountScope, DiscountStatus
from .models import GlobalDiscount, DiscountService

__all__ = [
    'DiscountType',
    'DiscountScope',
    'DiscountStatus',
    'GlobalDiscount',
    'DiscountService'
]
