"""
Affiliate discount code system.

This module provides functionality for managing and applying affiliate-specific
discount codes that can be used for marketing and promotions.
"""

from .models import AffiliateDiscount, AffiliateDiscountCreate, AffiliateDiscountUpdate

__all__ = [
    'AffiliateDiscount',
    'AffiliateDiscountCreate',
    'AffiliateDiscountUpdate'
]
