"""
Cart summary model for order calculations.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, root_validator

class CartSummary(BaseModel):
    """Summary of the cart's contents and costs."""
    subtotal: float = Field(
        0.0,
        ge=0,
        description="Sum of all item prices before discounts and shipping"
    )
    shipping: float = Field(
        0.0,
        ge=0,
        description="Total shipping cost"
    )
    tax: float = Field(
        0.0,
        ge=0,
        description="Total tax amount"
    )
    discount: float = Field(
        0.0,
        ge=0,
        description="Total discount amount"
    )
    total: float = Field(
        0.0,
        ge=0,
        description="Grand total (subtotal + shipping + tax - discount)"
    )
    item_count: int = Field(
        0,
        ge=0,
        alias="itemCount",
        description="Number of unique items in the cart"
    )
    total_quantity: int = Field(
        0,
        ge=0,
        alias="totalQuantity",
        description="Total quantity of all items"
    )
    requires_shipping: bool = Field(
        False,
        alias="requiresShipping",
        description="Whether any items in the cart require shipping"
    )
    currency: str = Field(
        "USD",
        description="Currency code for all monetary values"
    )
    
    # Shipping information
    shipping_options: List[Any] = Field(
        default_factory=list,
        alias="shippingOptions",
        description="Available shipping options"
    )
    selected_shipping_option: Optional[Any] = Field(
        None,
        alias="selectedShippingOption",
        description="Currently selected shipping option"
    )
    
    # Discount information
    discount_code: Optional[str] = Field(
        None,
        alias="discountCode",
        description="Applied discount code"
    )
    
    # Tax information
    tax_rate: Optional[float] = Field(
        None,
        alias="taxRate",
        ge=0,
        le=100,
        description="Applied tax rate as a percentage"
    )
    
    # Validators
    @root_validator
    def calculate_totals(cls, values):
        """Calculate derived values."""
        subtotal = values.get('subtotal', 0)
        shipping = values.get('shipping', 0)
        tax = values.get('tax', 0)
        discount = values.get('discount', 0)
        
        # Ensure tax is calculated if we have a rate but no tax amount
        if 'tax' not in values and 'tax_rate' in values and values['tax_rate'] is not None:
            tax = (subtotal - discount) * (values['tax_rate'] / 100)
            values['tax'] = max(0, tax)
        
        # Calculate total
        values['total'] = max(0, subtotal + shipping + tax - discount)
        
        return values
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            'datetime': lambda v: v.isoformat(),
        }
