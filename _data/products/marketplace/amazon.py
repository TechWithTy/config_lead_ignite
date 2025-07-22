"""
Models for Amazon product data and integration.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime

class AmazonDiscount(BaseModel):
    """Discount information for an Amazon product."""
    type: str = Field(..., description="Type of discount (e.g., 'PERCENT_OFF', 'AMOUNT_OFF')")
    amount: float = Field(..., ge=0, description="Discount amount")
    description: Optional[str] = Field(None, description="Description of the discount")
    valid_until: Optional[datetime] = Field(
        None,
        alias="validUntil",
        description="When the discount expires"
    )

class AmazonShippingOption(BaseModel):
    """Shipping options for an Amazon product."""
    method: str = Field(..., description="Shipping method name")
    cost: float = Field(..., ge=0, description="Shipping cost")
    estimated_arrival: str = Field(
        ...,
        alias="estimatedArrival",
        description="Estimated delivery date range"
    )
    is_prime_eligible: bool = Field(
        False,
        alias="isPrimeEligible",
        description="Whether this shipping option is Prime eligible"
    )
    is_free: bool = Field(
        False,
        alias="isFree",
        description="Whether shipping is free"
    )

class AmazonFulfillment(BaseModel):
    """Fulfillment details for an Amazon product."""
    fulfilled_by_amazon: bool = Field(
        False,
        alias="fulfilledByAmazon",
        description="Whether the item is fulfilled by Amazon (FBA)"
    )
    dropshipped: bool = Field(
        False,
        description="Whether the item is dropshipped"
    )
    marketplace_id: Optional[str] = Field(
        None,
        alias="marketplaceId",
        description="Amazon Marketplace ID"
    )
    seller_guarantees: List[str] = Field(
        default_factory=list,
        alias="sellerGuarantees",
        description="Seller guarantees (e.g., 'A-to-z Guarantee')"
    )

class AmazonDropshippingItem(BaseModel):
    """Complete Amazon product listing for dropshipping."""
    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    brand: Optional[str] = Field(None, description="Product brand")
    images: List[HttpUrl] = Field(
        default_factory=list,
        description="List of product image URLs"
    )
    category: str = Field(..., description="Product category")
    
    class Price(BaseModel):
        """Pricing information for the product."""
        amount: float = Field(..., ge=0, description="Current price")
        currency: str = Field("USD", description="Currency code")
        original_amount: Optional[float] = Field(
            None,
            alias="originalAmount",
            ge=0,
            description="Original price before discount"
        )
        discounts: List[AmazonDiscount] = Field(
            default_factory=list,
            description="List of applicable discounts"
        )
        is_amazon_fulfilled: bool = Field(
            False,
            alias="isAmazonFulfilled",
            description="Whether the price includes FBA benefits"
        )
    
    price: Price = Field(..., description="Pricing details")
    
    class Seller(BaseModel):
        """Information about the seller."""
        name: str = Field(..., description="Seller name")
        seller_id: str = Field(..., alias="sellerId", description="Seller ID")
        rating: Optional[float] = Field(
            None,
            ge=0,
            le=5,
            description="Seller rating (0-5)"
        )
        is_prime: bool = Field(
            False,
            alias="isPrime",
            description="Whether the seller is Prime eligible"
        )
        ships_from: Optional[str] = Field(
            None,
            alias="shipsFrom",
            description="Location where the seller ships from"
        )
        feedback_count: Optional[int] = Field(
            None,
            alias="feedbackCount",
            ge=0,
            description="Number of feedback ratings"
        )
    
    seller: Seller = Field(..., description="Product seller information")
    
    class Availability(BaseModel):
        """Product availability information."""
        is_in_stock: bool = Field(
            False,
            alias="isInStock",
            description="Whether the item is in stock"
        )
        estimated_delivery: Optional[str] = Field(
            None,
            alias="estimatedDelivery",
            description="Estimated delivery date range"
        )
        quantity_available: Optional[int] = Field(
            None,
            alias="quantityAvailable",
            ge=0,
            description="Number of items available"
        )
        is_prime_exclusive: bool = Field(
            False,
            alias="isPrimeExclusive",
            description="Whether the item is exclusive to Prime members"
        )
    
    availability: Availability = Field(..., description="Product availability details")
    
    class Shipping(BaseModel):
        """Shipping information for the product."""
        options: List[AmazonShippingOption] = Field(
            default_factory=list,
            description="Available shipping methods"
        )
        ships_from: str = Field(
            ...,
            alias="shipsFrom",
            description="Location where the item ships from"
        )
        ships_to: List[str] = Field(
            default_factory=list,
            alias="shipsTo",
            description="List of countries/regions where the item ships to"
        )
        handling_time_days: Optional[int] = Field(
            None,
            alias="handlingTimeDays",
            ge=0,
            description="Number of days required to process the order"
        )
        is_free_shipping_eligible: bool = Field(
            False,
            alias="isFreeShippingEligible",
            description="Whether the item is eligible for free shipping"
        )
    
    shipping: Shipping = Field(..., description="Shipping details")
    fulfillment: AmazonFulfillment = Field(..., description="Fulfillment information")
    
    # Additional fields
    features: List[str] = Field(
        default_factory=list,
        description="List of product features"
    )
    specifications: Dict[str, Any] = Field(
        default_factory=dict,
        description="Product specifications and details"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        alias="lastUpdated",
        description="When the product data was last updated"
    )

    @validator('price')
    def validate_price(cls, v):
        """Ensure price is valid."""
        if v.original_amount is not None and v.amount > v.original_amount:
            raise ValueError("Current price cannot be higher than original price")
        return v
