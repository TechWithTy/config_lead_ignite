"""Service layer for discount code operations."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Dict, Any, Union, Tuple
from uuid import UUID

from .models import GlobalDiscount, BaseDiscount
from .enums import DiscountStatus, DiscountType


class DiscountService:
    """Service for managing and applying discount codes."""
    
    def __init__(self, storage_adapter=None):
        """Initialize with an optional storage adapter."""
        self.storage = storage_adapter
    
    async def validate_discount_code(
        self,
        code: str,
        *,
        product_id: Optional[str] = None,
        category_id: Optional[str] = None,
        affiliate_id: Optional[str] = None,
        user_id: Optional[Union[str, UUID, int]] = None,
        amount: Optional[Union[Decimal, float, int, str]] = None
    ) -> Tuple[bool, Optional[BaseDiscount], str]:
        """
        Validate a discount code against the given criteria.
        
        Args:
            code: The discount code to validate
            product_id: The product ID the code is being applied to
            category_id: The category ID the code is being applied to
            affiliate_id: The affiliate ID (if any)
            user_id: The user ID applying the code (can be string, UUID, or int)
            amount: The purchase amount (for minimum purchase validation)
            
        Returns:
            Tuple of (is_valid, discount, message)
        """
        # Get the discount from storage
        discount = await self._get_discount_by_code(code)
        if not discount:
            return False, None, "Invalid discount code"
        
        # Convert amount to Decimal if provided
        if amount is not None and not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount))
            except (TypeError, InvalidOperation):
                return False, discount, "Invalid amount format"
        
        # Check if code is active and can be used by this user
        if not discount.is_active:
            return False, discount, "This code is no longer active"
            
        # Check overall usage limits
        if discount.max_uses is not None and discount.used_count >= discount.max_uses:
            return False, discount, "This code has reached its usage limit"
        
        # Check per-user usage limits
        if user_id and hasattr(discount, 'max_uses_per_user') and discount.max_uses_per_user:
            user_usage = await self._get_user_usage(discount, str(user_id))
            if user_usage >= discount.max_uses_per_user:
                return False, discount, "You have already used this code the maximum number of times"
        
        # Check date validity
        now = datetime.now(timezone.utc)
        if now < discount.start_date:
            return False, discount, "This code is not yet valid"
            
        if discount.end_date and now > discount.end_date:
            return False, discount, "This code has expired"
        
        # Check minimum purchase amount
        if amount is not None and discount.min_purchase_amount is not None:
            try:
                if amount < Decimal(str(discount.min_purchase_amount)):
                    return (
                        False,
                        discount,
                        f"Minimum purchase amount of {discount.min_purchase_amount} required"
                    )
            except (TypeError, InvalidOperation) as e:
                return False, discount, f"Invalid amount or minimum purchase amount: {str(e)}"
        
        # Check product restrictions
        if hasattr(discount, 'allowed_products') and discount.allowed_products:
            if product_id and product_id not in discount.allowed_products:
                return False, discount, "This code is not valid for the selected product"
        
        if hasattr(discount, 'excluded_products') and product_id in getattr(discount, 'excluded_products', []):
            return False, discount, "This code is not valid for the selected product"
        
        # Check category restrictions
        if hasattr(discount, 'allowed_categories') and discount.allowed_categories:
            if not category_id or category_id not in discount.allowed_categories:
                return False, discount, "This code is not valid for the selected category"
        
        if hasattr(discount, 'excluded_categories') and category_id in getattr(discount, 'excluded_categories', []):
            return False, discount, "This code is not valid for the selected category"
        
        # Check affiliate restrictions
        if hasattr(discount, 'affiliate_id') and discount.affiliate_id:
            if not affiliate_id or str(affiliate_id) != str(discount.affiliate_id):
                return False, discount, "This code is not valid for your account"
        
        return True, discount, "Valid discount code"
    
    async def apply_discount(
        self,
        code: str,
        amount: Union[Decimal, float, int, str],
        user_id: Optional[Union[str, UUID, int]] = None,
        **kwargs
    ) -> Tuple[bool, Decimal, Optional[BaseDiscount], str]:
        """
        Apply a discount code to an amount with user-specific tracking.
        
        Args:
            code: The discount code to apply
            amount: The original amount (can be Decimal, float, int, or string)
            user_id: The ID of the user applying the code (for usage tracking)
            **kwargs: Additional validation parameters (product_id, category_id, etc.)
            
        Returns:
            Tuple of (success, discounted_amount, discount, message)
        """
        # Convert amount to Decimal if needed
        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount))
            except (TypeError, InvalidOperation) as e:
                return False, Decimal('0'), None, f"Invalid amount format: {str(e)}"
        
        # Validate the discount code
        is_valid, discount, message = await self.validate_discount_code(
            code, **kwargs, amount=amount, user_id=user_id
        )
        
        if not is_valid or not discount:
            return False, amount, discount, message
        
        try:
            # Apply discount based on type
            if discount.discount_type == DiscountType.PERCENTAGE:
                discount_amount = (amount * discount.discount_value) / Decimal('100')
                new_amount = amount - discount_amount
            else:  # FIXED_AMOUNT
                discount_amount = min(discount.discount_value, amount)
                new_amount = amount - discount_amount
            
            # Ensure amount doesn't go below zero
            new_amount = max(Decimal('0'), new_amount)
            
            # Record the usage with user tracking
            await self._record_discount_usage(discount, str(user_id) if user_id else None)
            
            return True, new_amount, discount, "Discount applied successfully"
            
        except Exception as e:
            return False, amount, discount, f"Error applying discount: {str(e)}"
    
    async def _get_discount_by_code(self, code: str) -> Optional[BaseDiscount]:
        """Get a discount by its code from storage."""
        if self.storage:
            return await self.storage.get_discount_by_code(code)
        # Fallback to in-memory or other storage if needed
        return None
    
    async def _get_user_usage(self, discount: BaseDiscount, user_id: str) -> int:
        """Get the number of times a user has used a discount code."""
        if self.storage and hasattr(self.storage, 'get_user_usage'):
            return await self.storage.get_user_usage(discount.code, user_id)
        # Fallback to in-memory tracking if available
        return getattr(discount, 'get_user_usage_count', lambda _: 0)(user_id)
    
    async def _record_discount_usage(
        self, 
        discount: BaseDiscount, 
        user_id: Optional[str] = None
    ) -> None:
        """
        Record that a discount code has been used, with optional user tracking.
        
        Args:
            discount: The discount code that was used
            user_id: Optional user ID for per-user tracking
        """
        if self.storage:
            # Use storage adapter if available
            await self.storage.record_usage(discount.code, user_id)
        else:
            # Fallback to in-memory tracking
            if hasattr(discount, 'record_usage'):
                discount.record_usage(user_id)
            else:
                # Basic fallback if record_usage method not available
                discount.used_count += 1
