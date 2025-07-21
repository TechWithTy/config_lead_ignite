"""Request and response schemas for the affiliate API."""
from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator, condecimal
from .models import (
    AffiliateProfile,
    BankAccountInfo,
    TaxInfo,
    AffiliatePayout,
    AffiliateReferral,
    AffiliateNotificationPreferences,
)
from .enums import (
    NetworkSize,
    AccountType,
    AffiliateStatus,
    RealEstateExperience,
    PaymentMethod,
    PayoutSchedule,
    CommissionTier,
)

# Request Schemas
class AffiliateCreateRequest(BaseModel):
    """Schema for creating a new affiliate."""
    user_id: str = Field(..., description="ID of the user becoming an affiliate")
    network_size: NetworkSize = Field(..., description="Size of the affiliate's network")
    social_handle: str = Field(..., min_length=2, max_length=50,
                             description="Primary social media handle")
    website: Optional[HttpUrl] = Field(None, description="Affiliate's website or blog")
    real_estate_experience: RealEstateExperience = Field(
        ...,
        description="Level of real estate experience"
    )
    custom_promo_code: Optional[str] = Field(
        None,
        min_length=4,
        max_length=20,
        regex=r'^[A-Z0-9_-]+$',
        description="Custom promotional code (optional)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "usr_1234567890",
                "network_size": "1,001-10,000",
                "social_handle": "@realestatepro",
                "website": "https://myrealestatesite.com",
                "real_estate_experience": "yes",
                "custom_promo_code": "REALESTATE15"
            }
        }

class BankAccountCreateRequest(BaseModel):
    """Schema for adding a bank account."""
    bank_name: str = Field(..., min_length=2, max_length=100)
    account_holder_name: str = Field(..., min_length=2, max_length=100)
    routing_number: str = Field(..., regex=r'^\d{9}$')
    account_number: str = Field(..., min_length=4, max_length=17)
    account_type: AccountType = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "bank_name": "Chase Bank",
                "account_holder_name": "John Doe",
                "routing_number": "021000021",
                "account_number": "1234567890",
                "account_type": "checking"
            }
        }

class TaxInfoRequest(BaseModel):
    """Schema for submitting tax information."""
    tax_id: str = Field(..., min_length=9, max_length=11)
    tax_id_type: str = Field(..., description="SSN or EIN")
    tax_form_type: str = Field(..., description="e.g., W-9, W-8BEN, etc.")
    is_us_person: bool = Field(True)
    
    class Config:
        schema_extra = {
            "example": {
                "tax_id": "123-45-6789",
                "tax_id_type": "SSN",
                "tax_form_type": "W-9",
                "is_us_person": True
            }
        }

class PayoutRequest(BaseModel):
    """Schema for requesting a payout."""
    amount: condecimal(ge=10.00, max_digits=12, decimal_places=2) = Field(
        ...,
        description="Minimum $10.00"
    )
    payment_method: PaymentMethod = Field(...)
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Any notes about this payout request"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "amount": 150.75,
                "payment_method": "bank_transfer",
                "notes": "Monthly commission payout"
            }
        }

class ReferralCreateRequest(BaseModel):
    """Schema for creating a new referral."""
    referred_email: EmailStr = Field(...)
    referral_code: str = Field(..., min_length=4, max_length=20)
    source: str = Field("direct")
    campaign: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the referral"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "referred_email": "newuser@example.com",
                "referral_code": "WELCOME10",
                "source": "email",
                "campaign": "summer2023",
                "metadata": {
                    "utm_source": "newsletter",
                    "utm_medium": "email"
                }
            }
        }

# Response Schemas
class AffiliateResponse(AffiliateProfile):
    """Response schema for affiliate profile."""
    class Config:
        fields = {
            'bank_account': {'exclude': True},
            'tax_info': {'exclude': True}
        }
        json_encoders = {
            'secret': lambda v: '***' if v else None
        }

class BankAccountResponse(BankAccountInfo):
    """Response schema for bank account details."""
    class Config:
        fields = {
            'routing_number': {'exclude': True},
            'account_number': {'exclude': True}
        }

class PayoutResponse(AffiliatePayout):
    """Response schema for payout details."""
    pass

class ReferralResponse(AffiliateReferral):
    """Response schema for referral details."""
    pass

class DashboardStatsResponse(BaseModel):
    """Response schema for affiliate dashboard statistics."""
    total_commissions: condecimal(max_digits=12, decimal_places=2)
    pending_payout: condecimal(max_digits=12, decimal_places=2)
    lifetime_earnings: condecimal(max_digits=12, decimal_places=2)
    total_referrals: int
    active_referrals: int
    conversion_rate: float
    next_payout_date: Optional[date]
    payout_threshold: condecimal(max_digits=12, decimal_places=2)
    
    class Config:
        schema_extra = {
            "example": {
                "total_commissions": 1250.75,
                "pending_payout": 325.50,
                "lifetime_earnings": 3250.25,
                "total_referrals": 42,
                "active_referrals": 28,
                "conversion_rate": 0.67,
                "next_payout_date": "2023-07-31",
                "payout_threshold": 50.00
            }
        }

class CommissionTierInfo(BaseModel):
    """Information about a commission tier."""
    tier: str
    rate: float
    min_referrals: int
    min_commission: float
    benefits: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "tier": "silver",
                "rate": 0.15,
                "min_referrals": 10,
                "min_commission": 1000.00,
                "benefits": [
                    "15% commission rate",
                    "Priority support",
                    "Early access to new features"
                ]
            }
        }

# Update Schemas
class AffiliateUpdateRequest(BaseModel):
    """Schema for updating affiliate profile."""
    network_size: Optional[NetworkSize] = None
    social_handle: Optional[str] = Field(None, min_length=2, max_length=50)
    website: Optional[HttpUrl] = None
    custom_promo_code: Optional[str] = Field(
        None,
        min_length=4,
        max_length=20,
        regex=r'^[A-Z0-9_-]+$'
    )
    notification_prefs: Optional[AffiliateNotificationPreferences] = None
    
    class Config:
        schema_extra = {
            "example": {
                "social_handle": "@newhandle",
                "website": "https://mynewwebsite.com",
                "notification_prefs": {
                    "email_newsletter": False,
                    "sms_important_updates": True
                }
            }
        }

# Admin Schemas
class AdminAffiliateUpdateRequest(BaseModel):
    """Admin-only schema for updating affiliate details."""
    status: Optional[AffiliateStatus] = None
    tier: Optional[CommissionTier] = None
    custom_commission_rate: Optional[float] = Field(
        None,
        ge=0.01,
        le=0.5,
        description="Custom commission rate (0.01-0.50)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Internal notes about this affiliate"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "approved",
                "tier": "silver",
                "custom_commission_rate": 0.12,
                "notes": "High-value affiliate with excellent conversion rates"
            }
        }
