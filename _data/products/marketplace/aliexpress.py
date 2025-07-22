"""
Models for AliExpress product data and integration.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime

class AliexpressShippingOption(BaseModel):
    """Shipping options available for an AliExpress product."""
    service: str = Field(..., description="Name of the shipping service")
    estimated_delivery_time: str = Field(
        ...,
        alias="estimatedDeliveryTime",
        description="Estimated delivery time range"
    )
    cost: float = Field(..., ge=0, description="Shipping cost in the specified currency")
    currency: str = Field("USD", description="Currency code (e.g., USD, EUR)")
    tracking_available: bool = Field(
        True,
        alias="trackingAvailable",
        description="Whether tracking is available for this shipping method"
    )
    ship_from: str = Field(
        ...,
        alias="shipFrom",
        description="Country/region where the item ships from"
    )
    ship_to: str = Field(
        ...,
        alias="shipTo",
        description="Country/region where the item ships to"
    )

class AliexpressVariantAttribute(BaseModel):
    """Attribute for a product variant (e.g., color, size)."""
    name: str = Field(..., description="Attribute name (e.g., 'Color', 'Size')")
    value: str = Field(..., description="Attribute value (e.g., 'Red', 'XL')")

class AliexpressVariant(BaseModel):
    """Product variant with specific attributes."""
    id: str = Field(..., description="Variant ID")
    sku: str = Field(..., description="Stock Keeping Unit for the variant")
    attributes: List[AliexpressVariantAttribute] = Field(
        default_factory=list,
        description="List of variant attributes"
    )

class AliexpressDropshippingItem(BaseModel):
    """Complete AliExpress product listing for dropshipping."""
    id: str = Field(..., description="Product ID on AliExpress")
    title: str = Field(..., description="Product title/name")
    description: str = Field(..., description="Product description (HTML supported)")
    category_id: str = Field(..., alias="categoryId", description="Category ID")
    category_name: str = Field(..., alias="categoryName", description="Category name")
    sku: str = Field(..., description="Product SKU")
    item_url: HttpUrl = Field(..., alias="itemUrl", description="URL to the product page")
    images: List[HttpUrl] = Field(
        default_factory=list,
        description="List of product image URLs"
    )
    video_url: Optional[HttpUrl] = Field(
        None,
        alias="videoUrl",
        description="URL to product video if available"
    )
    
    class Price(BaseModel):
        """Pricing information for the product."""
        currency: str = Field("USD", description="Currency code")
        original: float = Field(..., ge=0, description="Original price")
        discounted: float = Field(..., ge=0, description="Current discounted price")
        min: float = Field(..., ge=0, description="Minimum price (for variants)")
        max: float = Field(..., ge=0, description="Maximum price (for variants)")
    
    price: Price = Field(..., description="Pricing details")
    
    available_quantity: int = Field(
        ...,
        alias="availableQuantity",
        ge=0,
        description="Number of items available for purchase"
    )
    min_order_quantity: int = Field(
        1,
        alias="minOrderQuantity",
        ge=1,
        description="Minimum order quantity"
    )
    shipping_options: List[AliexpressShippingOption] = Field(
        default_factory=list,
        alias="shippingOptions",
        description="Available shipping methods"
    )
    variants: List[AliexpressVariant] = Field(
        default_factory=list,
        description="Product variants if available"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        alias="lastUpdated",
        description="When the product data was last updated"
    )

    @validator('price')
    def validate_price_ranges(cls, v):
        """Ensure price ranges are valid."""
        if v.discounted > v.original:
            raise ValueError("Discounted price cannot be higher than original price")
        if v.min > v.max:
            raise ValueError("Minimum price cannot be greater than maximum price")
        return v
