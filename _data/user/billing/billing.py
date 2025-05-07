"""
BillingInfo and PaymentInfo models for storing user billing and payment details separately.
"""
from pydantic import BaseModel, Field
from typing import Optional

class PaymentInfo(BaseModel):
    """Stores payment method details for the user."""
    payment_method_id: Optional[str] = Field(None, description="Payment method reference (e.g., Stripe ID)")
    card_last4: Optional[str] = Field(None, description="Last 4 digits of card on file")
    card_brand: Optional[str] = Field(None, description="Card brand (Visa, Mastercard, etc.)")
    card_expiry: Optional[str] = Field(None, description="Card expiration (MM/YY)")
    default: bool = Field(True, description="Is this the default billing method?")

class BillingInfo(BaseModel):
    """Stores billing address and account information for the user."""
    billing_name: str = Field(..., description="Name on the billing account")
    billing_email: str = Field(..., description="Billing email address")
    address_line1: str = Field(..., description="Billing address line 1")
    address_line2: Optional[str] = Field(None, description="Billing address line 2 (optional)")
    city: str = Field(..., description="Billing city")
    state: str = Field(..., description="Billing state/province/region")
    postal_code: str = Field(..., description="Billing postal or zip code")
    country: str = Field(..., description="Billing country")
    company_name: Optional[str] = Field(None, description="Company name (if applicable)")
    vat_id: Optional[str] = Field(None, description="VAT or tax ID")
    phone: Optional[str] = Field(None, description="Billing phone number")
    payment_info: Optional[PaymentInfo] = Field(None, description="Payment method details")
