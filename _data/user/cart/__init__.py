"""
Cart models for managing user shopping carts.

This package provides Pydantic models for handling shopping cart functionality,
including cart items, summaries, and state management.
"""
from .exceptions import CartError
from .models import ProductVariant, CartItem, CartSummary, CartState

# Default empty cart summary
DEFAULT_CART_SUMMARY = CartSummary()

__all__ = [
    'CartError',
    'ProductVariant',
    'CartItem',
    'CartSummary',
    'CartState',
    'DEFAULT_CART_SUMMARY'
]
