"""
Models for supplier and contact information.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr

class SupplierContactInfo(BaseModel):
    """Contact information for a supplier or vendor."""
    email: Optional[EmailStr] = Field(
        None,
        description="Primary contact email address"
    )
    whatsapp: Optional[str] = Field(
        None,
        description="WhatsApp contact number in international format"
    )
    phone: Optional[str] = Field(
        None,
        description="Primary contact phone number"
    )
    website: Optional[HttpUrl] = Field(
        None,
        description="Company website URL"
    )
    social_profile_url: Optional[HttpUrl] = Field(
        None,
        alias="socialProfileUrl",
        description="URL to primary social media profile"
    )
    address: Optional[str] = Field(
        None,
        description="Physical business address"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional contact information or notes"
    )

class SupplierVerification(BaseModel):
    """Verification details for a supplier."""
    is_verified: bool = Field(
        default=False,
        alias="isVerified",
        description="Whether the supplier has been verified"
    )
    verified_at: Optional[datetime] = Field(
        None,
        alias="verifiedAt",
        description="When the supplier was verified"
    )
    verified_by: Optional[str] = Field(
        None,
        alias="verifiedBy",
        description="Who verified the supplier"
    )
    documents: List[str] = Field(
        default_factory=list,
        description="List of document IDs used for verification"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional verification notes"
    )

class DropshippingIntegration(BaseModel):
    """Dropshipping integration details for a product."""
    supplier_url: HttpUrl = Field(
        ...,
        alias="supplierUrl",
        description="URL to the product on supplier's site"
    )
    purchase_cost: float = Field(
        ...,
        alias="purchaseCost",
        ge=0,
        description="Cost to purchase the item from supplier"
    )
    resale_price: float = Field(
        ...,
        alias="resalePrice",
        ge=0,
        description="Price at which the item is sold to customers"
    )
    profit_margin: float = Field(
        ...,
        alias="profitMargin",
        description="Calculated profit margin percentage"
    )
    last_synced: datetime = Field(
        ...,
        alias="lastSynced",
        description="When the product data was last synced with supplier"
    )
    supplier_contact: Optional[SupplierContactInfo] = Field(
        None,
        alias="supplierContact",
        description="Contact information for the supplier"
    )
    verification: Optional[SupplierVerification] = Field(
        None,
        description="Verification status of the supplier"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "supplierUrl": "https://example.com/product123",
                "purchaseCost": 10.99,
                "resalePrice": 24.99,
                "profitMargin": 127.39,
                "lastSynced": "2023-01-01T12:00:00Z",
                "supplierContact": {
                    "email": "supplier@example.com",
                    "phone": "+1234567890"
                },
                "verification": {
                    "isVerified": True,
                    "verifiedAt": "2023-01-01T00:00:00Z"
                }
            }
        }
