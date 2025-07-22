"""
Cart item model representing a product in the shopping cart.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator

from ..exceptions import CartError
from .product_variant import ProductVariant

class CartItem(BaseModel):
    """An item in the shopping cart."""
    # Core product information
    id: str = Field(..., description="Unique identifier for the cart item")
    product_id: str = Field(
        ...,
        alias="productId",
        description="Reference to the product"
    )
    name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Unit price")
    
    # Variant information
    selected_variant: Optional[ProductVariant] = Field(
        None,
        alias="selectedVariant",
        description="Selected product variant"
    )
    
    # Quantity and pricing
    quantity: int = Field(
        1,
        ge=1,
        description="Quantity of this item in the cart"
    )
    subtotal: float = Field(
        ...,
        ge=0,
        description="Total price for this line item (price * quantity)"
    )
    
    # Shipping and inventory
    requires_shipping: bool = Field(
        True,
        alias="requiresShipping",
        description="Whether this item requires shipping"
    )
    in_stock: bool = Field(
        True,
        alias="inStock",
        description="Whether the item is currently in stock"
    )
    
    # Metadata
    image: Optional[str] = Field(
        None,
        description="URL of the product image"
    )
    category: Optional[str] = Field(
        None,
        description="Product category"
    )
    notes: Optional[str] = Field(
        None,
        description="Customer notes or customization requests"
    )
    added_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="addedAt",
        description="When the item was added to the cart"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this cart item"
    )
    
    # Computed properties
    @property
    def variant_id(self) -> Optional[str]:
        """Get the variant ID if available."""
        return self.selected_variant.id if self.selected_variant else None
    
    @property
    def unit_price(self) -> float:
        """Get the unit price, considering variant pricing if available."""
        if self.selected_variant and self.selected_variant.price is not None:
            return self.selected_variant.price
        return self.price
    
    # Validators
    @root_validator(pre=True)
    def calculate_subtotal(cls, values):
        """Calculate subtotal based on quantity and unit price."""
        if 'subtotal' not in values:
            quantity = values.get('quantity', 1)
            unit_price = (
                values.get('selected_variant', {}).get('price')
                or values.get('price', 0)
            )
            values['subtotal'] = quantity * unit_price
        return values
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Ensure quantity is at least 1."""
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
