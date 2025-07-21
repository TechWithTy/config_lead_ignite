"""Enums for the discount system."""

from enum import Enum, auto
from typing import Any


class DiscountType(str, Enum):
    """Type of discount to apply."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class DiscountScope(str, Enum):
    """Scope of the discount's applicability."""
    GLOBAL = "global"
    PRODUCT = "product"
    CATEGORY = "category"
    AFFILIATE = "affiliate"


class DiscountStatus(str, Enum):
    """Status of a discount code."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    USAGE_LIMIT_REACHED = "usage_limit_reached"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        """Handle case-insensitive enum value lookups."""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return super()._missing_(value)
