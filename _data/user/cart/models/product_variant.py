"""
Product variant model for cart items.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ProductVariant(BaseModel):
    """Selected variant of a product in the cart."""
    id: str = Field(..., description="Unique identifier for the variant")
    name: str = Field(..., description="Display name of the variant")
    price: float = Field(..., ge=0, description="Price of this variant")
    requires_shipping: bool = Field(
        True,
        alias="requiresShipping",
        description="Whether this variant requires shipping"
    )
    sku: Optional[str] = Field(
        None,
        description="Stock Keeping Unit for this variant"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional variant-specific data"
    )

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
