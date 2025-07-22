"""
Core product models and related types.
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, validator

from .enums import LicenseType, ProductCategory

class Review(BaseModel):
    """Product review from customers."""
    id: int = Field(..., description="Unique review identifier")
    author: str = Field(..., description="Name of the reviewer")
    rating: float = Field(
        ...,
        ge=0,
        le=5,
        description="Rating from 0 to 5 stars"
    )
    date: date = Field(..., description="Date of the review")
    content: str = Field(..., description="Review text content")
    title: Optional[str] = Field(
        None,
        description="Optional title for the review"
    )
    image: Optional[HttpUrl] = Field(
        None,
        description="Image URL attached to the review"
    )
    verified_purchase: bool = Field(
        False,
        alias="verifiedPurchase",
        description="Whether the reviewer is a verified purchaser"
    )
    helpful_votes: int = Field(
        0,
        alias="helpfulVotes",
        description="Number of users who found this review helpful"
    )

class SalesIncentive(BaseModel):
    """Special offers or incentives for a product."""
    class IncentiveType(str, Enum):
        ON_SALE = "onSale"
        LIMITED_TIME = "limitedTime"
        CLEARANCE = "clearance"
        BUNDLE = "bundle"
        NEW_ARRIVAL = "newArrival"
        FREE_SHIPPING = "freeShipping"
        BULK_DISCOUNT = "bulkDiscount"
        SEASONAL = "seasonal"
        FLASH_SALE = "flashSale"
        
    type: IncentiveType = Field(..., description="Type of sales incentive")
    description: Optional[str] = Field(
        None,
        description="Description of the incentive"
    )
    discount_percent: Optional[float] = Field(
        None,
        alias="discountPercent",
        ge=0,
        le=100,
        description="Discount percentage (if applicable)"
    )
    expires_at: Optional[datetime] = Field(
        None,
        alias="expiresAt",
        description="When the incentive expires"
    )
    promo_code: Optional[str] = Field(
        None,
        alias="promoCode",
        description="Promo code for the incentive"
    )
    min_purchase: Optional[float] = Field(
        None,
        alias="minPurchase",
        ge=0,
        description="Minimum purchase amount to qualify"
    )

class ProductFaq(BaseModel):
    """Frequently asked question about a product."""
    question: str = Field(..., description="The question being asked")
    answer: str = Field(..., description="Answer to the question")
    category: Optional[str] = Field(
        None,
        description="Category of the FAQ (e.g., 'Shipping', 'Returns')"
    )
    last_updated: Optional[date] = Field(
        None,
        alias="lastUpdated",
        description="When this FAQ was last updated"
    )

class TechLicense(BaseModel):
    """License information for technology products."""
    name: str = Field(..., description="Name of the license")
    type: LicenseType = Field(..., description="Type of license")
    url: HttpUrl = Field(..., description="URL to license details")
    description: Optional[str] = Field(
        None,
        description="Brief description of the license"
    )
    version: Optional[str] = Field(
        None,
        description="Version of the license"
    )
    is_osi_approved: bool = Field(
        False,
        alias="isOsiApproved",
        description="Whether the license is OSI approved"
    )

class SizingChartItem(BaseModel):
    """Item in a product sizing chart."""
    label: str = Field(..., description="Row/column label")
    value: Union[str, float, int] = Field(..., description="Value for this item")
    measurement: str = Field(..., description="Type of measurement")
    unit: str = Field(..., description="Unit of measurement")
    description: Optional[str] = Field(
        None,
        description="Additional description or notes"
    )

class ProductVariantType(BaseModel):
    """Type of product variant."""
    name: str = Field(..., description="Name of the variant type")
    value: str = Field(..., description="Value of the variant")
    price: float = Field(0.0, description="Additional price for this variant")
    sku: Optional[str] = Field(
        None,
        description="SKU for this specific variant"
    )
    image: Optional[HttpUrl] = Field(
        None,
        description="Image specific to this variant"
    )

class ProductColorVariant(BaseModel):
    """Color variant of a product."""
    name: str = Field(..., description="Name of the color")
    value: str = Field(..., description="Color value (hex, RGB, etc.)")
    class_name: str = Field(
        ...,
        alias="class",
        description="CSS class for displaying the color"
    )
    image: Optional[HttpUrl] = Field(
        None,
        description="Image showing this color variant"
    )
    in_stock: bool = Field(
        True,
        alias="inStock",
        description="Whether this color is in stock"
    )

class ProductSizeVariant(BaseModel):
    """Size variant of a product."""
    name: str = Field(..., description="Display name of the size")
    value: str = Field(..., description="Value of the size")
    in_stock: bool = Field(
        True,
        alias="inStock",
        description="Whether this size is in stock"
    )
    sku: Optional[str] = Field(
        None,
        description="SKU for this specific size"
    )
    dimensions: Optional[Dict[str, str]] = Field(
        None,
        description="Dimensions for this size"
    )

class ProductType(BaseModel):
    """Core product type with all variants and options."""
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Detailed product description")
    price: float = Field(..., ge=0, description="Base price")
    sku: str = Field(..., description="Stock Keeping Unit")
    slug: Optional[str] = Field(
        None,
        description="URL-friendly version of the name"
    )
    images: List[HttpUrl] = Field(
        default_factory=list,
        description="List of product image URLs"
    )
    reviews: List[Review] = Field(
        default_factory=list,
        description="Customer reviews"
    )
    sales_incentive: Optional[SalesIncentive] = Field(
        None,
        alias="salesIncentive",
        description="Current sales incentive if any"
    )
    sizing_chart: Optional[List[SizingChartItem]] = Field(
        None,
        alias="sizingChart",
        description="Sizing information for the product"
    )
    categories: List[ProductCategory] = Field(
        default_factory=list,
        description="Product categories"
    )
    license_name: Optional[LicenseType] = Field(
        None,
        alias="licenseName",
        description="Software license if applicable"
    )
    types: List[ProductVariantType] = Field(
        default_factory=list,
        description="Available product types/variants"
    )
    colors: List[ProductColorVariant] = Field(
        default_factory=list,
        description="Available color options"
    )
    sizes: List[ProductSizeVariant] = Field(
        default_factory=list,
        description="Available size options"
    )
    faqs: List[ProductFaq] = Field(
        default_factory=list,
        description="Frequently asked questions"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable product tags"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="createdAt",
        description="When the product was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="updatedAt",
        description="When the product was last updated"
    )
    is_active: bool = Field(
        True,
        alias="isActive",
        description="Whether the product is active and visible"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional product metadata"
    )

    @validator('slug', always=True)
    def generate_slug(cls, v, values):
        """Generate slug from name if not provided."""
        if not v and 'name' in values:
            return values['name'].lower().replace(' ', '-')
        return v
