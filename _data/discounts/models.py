"""Pydantic models for the global discount system."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator

from .enums import DiscountType, DiscountScope, DiscountStatus


class BaseDiscount(BaseModel):
    """Base discount model with common fields and validation."""
    
    code: str = Field(
        ..., 
        min_length=4, 
        max_length=50, 
        regex=r'^[A-Z0-9_-]+$',
        description="Unique discount code (uppercase alphanumeric with hyphens/underscores)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=500,
        description="Description of the discount code"
    )
    discount_type: DiscountType = Field(
        ...,
        description="Type of discount (percentage or fixed amount)"
    )
    discount_value: Decimal = Field(
        ..., 
        gt=0,
        description="The value of the discount (percentage or fixed amount)"
    )
    max_uses: Optional[int] = Field(
        None, 
        gt=0,
        description="Maximum number of times this code can be used in total (None = no limit)"
    )
    max_uses_per_user: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum number of times a single user can use this code (None = no limit)"
    )
    used_count: int = Field(
        0, 
        ge=0,
        description="Total number of times this code has been used"
    )
    _user_usage: Dict[str, int] = Field(
        default_factory=dict,
        description="Tracks usage count per user ID (internal use only)",
        exclude=True
    )
    start_date: datetime = Field(
        ...,
        description="When the discount code becomes active"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="When the discount code expires (None = no expiration)"
    )
    is_active: bool = Field(
        True,
        description="Whether the discount code is currently active"
    )
    min_purchase_amount: Optional[Decimal] = Field(
        None, 
        gt=0,
        description="Minimum purchase amount required to use this code"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the discount code"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the discount code was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the discount code was last updated"
    )

    @validator('discount_value')
    def validate_discount_value(cls, v: Decimal, values: Dict[str, Any]) -> Decimal:
        """Validate discount value based on discount type."""
        if 'discount_type' in values and values['discount_type'] == DiscountType.PERCENTAGE:
            if v > 100:
                raise ValueError('Percentage discount cannot exceed 100%')
        return v

    @validator('end_date')
    def validate_dates(cls, v: Optional[datetime], values: Dict[str, Any]) -> Optional[datetime]:
        """Validate that end date is after start date if both are provided."""
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @root_validator
    def update_timestamps(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update the updated_at timestamp."""
        values['updated_at'] = datetime.utcnow()
        return values
    
    def get_user_usage_count(self, user_id: str) -> int:
        """Get the number of times a specific user has used this code."""
        return self._user_usage.get(str(user_id), 0)
    
    def can_user_use_code(self, user_id: Optional[str] = None) -> bool:
        """Check if a user can use this discount code."""
        if not self.is_active:
            return False
            
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
            
        if user_id and self.max_uses_per_user is not None:
            user_usage = self.get_user_usage_count(user_id)
            if user_usage >= self.max_uses_per_user:
                return False
                
        now = datetime.now(timezone.utc)
        if now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return True
    
    def record_usage(self, user_id: Optional[str] = None) -> None:
        """Record that this code has been used by a user."""
        self.used_count += 1
        
        if user_id:
            user_id_str = str(user_id)
            self._user_usage[user_id_str] = self.get_user_usage_count(user_id_str) + 1
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now(timezone.utc)
    
    @property
    def status(self) -> DiscountStatus:
        """Get the current status of the discount code."""
        now = datetime.now(timezone.utc)
        
        if not self.is_active:
            return DiscountStatus.INACTIVE
            
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return DiscountStatus.USAGE_LIMIT_REACHED
            
        if self.end_date and now > self.end_date:
            return DiscountStatus.EXPIRED
            
        if now < self.start_date:
            return DiscountStatus.INACTIVE
            
        return DiscountStatus.ACTIVE
    
    def is_usable(self) -> bool:
        """Check if the discount code is currently usable."""
        return self.status == DiscountStatus.ACTIVE


class GlobalDiscount(BaseDiscount):
    """Global discount codes that can be applied to any purchase."""
    
    scope: DiscountScope = Field(
        DiscountScope.GLOBAL,
        description="Scope of the discount's applicability"
    )
    allowed_products: List[str] = Field(
        default_factory=list,
        description="List of product IDs this code applies to (empty = all products)"
    )
    excluded_products: List[str] = Field(
        default_factory=list,
        description="List of product IDs this code does not apply to"
    )
    allowed_categories: List[str] = Field(
        default_factory=list,
        description="List of category IDs this code applies to (empty = all categories)"
    )
    excluded_categories: List[str] = Field(
        default_factory=list,
        description="List of category IDs this code does not apply to"
    )
    
    class Config:
        json_encoders = {
            Decimal: str
        }
        schema_extra = {
            "example": {
                "code": "SUMMER25",
                "description": "Summer Sale 25% Off",
                "discount_type": "percentage",
                "discount_value": "25.00",
                "start_date": "2023-06-01T00:00:00Z",
                "end_date": "2023-08-31T23:59:59Z",
                "max_uses": 1000,
                "min_purchase_amount": "50.00",
                "allowed_products": ["prod_123", "prod_456"],
                "excluded_products": ["prod_789"],
                "allowed_categories": ["clothing", "accessories"],
                "excluded_categories": ["sale"]
            }
        }
