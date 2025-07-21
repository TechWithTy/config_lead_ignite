"""Pydantic models for the affiliate system."""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional
from pydantic import (
    BaseModel, 
    Field, 
    HttpUrl, 
    validator, 
    root_validator
)
from .enums import (
    NetworkSize, 
    AccountType, 
    AffiliateStatus, 
    RealEstateExperience,
    PaymentMethod,
    PayoutSchedule,
    CommissionTier
)

class BankAccountInfo(BaseModel):
    """Sensitive bank account information for payouts."""
    bank_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Name of the financial institution"
    )
    account_holder_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Name as it appears on the account"
    )
    routing_number: str = Field(
        ..., 
        regex=r'^\d{9}$',
        description="9-digit routing number"
    )
    account_number: str = Field(
        ...,
        min_length=4,
        max_length=17,
        description="Account number"
    )
    account_type: AccountType = Field(..., 
                                    description="Type of bank account")
    last_four: str = Field(..., regex=r'^\d{4}$', 
                         description="Last 4 digits of account number")
    is_verified: bool = Field(False, description="If the account has been verified")
    verification_attempts: int = Field(0, ge=0, 
                                    description="Number of verification attempts")

    class Config:
        json_encoders = {
            'secret': lambda v: '***' if v else None
        }
        schema_extra = {
            "example": {
                "bank_name": "Chase Bank",
                "account_holder_name": "John Doe",
                "routing_number": "021000021",
                "account_number": "******1234",
                "account_type": "checking",
                "last_four": "1234",
                "is_verified": False,
                "verification_attempts": 0
            }
        }

class TaxInfo(BaseModel):
    """Tax information for affiliate payouts."""
    tax_id: Optional[str] = Field(None, min_length=9, max_length=11,
                                description="SSN or EIN (formatted)")
    tax_id_type: Optional[str] = Field(None, description="SSN or EIN")
    tax_form_received: Optional[date] = Field(None, 
                                           description="Date tax form was received")
    tax_form_type: Optional[str] = Field(None, 
                                      description="e.g., W-9, W-8BEN, etc.")
    tax_form_url: Optional[HttpUrl] = Field(None, 
                                         description="Link to stored tax form")
    is_us_person: bool = Field(True, 
                             description="Whether the affiliate is a US person for tax purposes")

class AffiliateProfile(BaseModel):
    """Main affiliate profile model."""
    id: str = Field(..., description="Unique identifier for the affiliate")
    user_id: str = Field(..., description="Reference to core user ID")
    network_size: NetworkSize = Field(..., 
                                   description="Size of the affiliate's network")
    social_handle: str = Field(..., min_length=2, max_length=50,
                             description="Primary social media handle")
    website: Optional[HttpUrl] = Field(None, 
                                     description="Affiliate's website or blog")
    commission_rate: Decimal = Field(
        default=Decimal('0.1'),
        ge=Decimal('0'),
        le=Decimal('1'),
        max_digits=5,
        decimal_places=4,
        description="Commission rate as decimal (e.g., 0.1 for 10%)"
    )
    tier: CommissionTier = Field(CommissionTier.STANDARD, 
                              description="Affiliate tier level")
    status: AffiliateStatus = Field(AffiliateStatus.PENDING, 
                                  description="Current status of the affiliate")
    is_active: bool = Field(True, 
                          description="Whether the affiliate is active")
    real_estate_experience: RealEstateExperience = Field(
        ...,
        description="Level of real estate experience"
    )
    custom_promo_code: Optional[str] = Field(
        None,
        min_length=4,
        max_length=20,
        regex=r'^[A-Z0-9_-]+$',
        description="Custom promotional code for the affiliate"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_payout_date: Optional[datetime] = Field(
        None,
        description="Date of the last successful payout"
    )
    next_payout_date: Optional[datetime] = Field(
        None,
        description="Scheduled date for the next payout"
    )
    payout_schedule: PayoutSchedule = Field(
        PayoutSchedule.MONTHLY,
        description="Preferred payout schedule"
    )
    minimum_payout: Decimal = Field(
        default=Decimal('50.00'),
        ge=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        description="Minimum balance required for payout"
    )
    
    # Relationships
    bank_account: Optional[BankAccountInfo] = None
    tax_info: Optional[TaxInfo] = None
    
    # Performance metrics (cached values)
    total_referrals: int = Field(0, ge=0)
    active_referrals: int = Field(0, ge=0)
    total_commissions: Decimal = Field(
        default=Decimal('0'),
        ge=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        description="Total commissions earned (in base currency)"
    )
    pending_payout: Decimal = Field(
        default=Decimal('0'),
        ge=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        description="Commissions awaiting payout"
    )
    lifetime_earnings: Decimal = Field(
        default=Decimal('0'),
        ge=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        description="Total earnings including paid out and pending"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            'secret': lambda v: '***' if v else None
        }
        schema_extra = {
            "example": {
                "id": "aff_1234567890",
                "user_id": "usr_1234567890",
                "network_size": "1,001-10,000",
                "social_handle": "@realestatepro",
                "website": "https://myrealestatesite.com",
                "commission_rate": 0.15,
                "tier": "silver",
                "status": "approved",
                "is_active": True,
                "real_estate_experience": "yes",
                "custom_promo_code": "REALESTATE15",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-06-15T10:30:00Z",
                "total_referrals": 42,
                "active_referrals": 28,
                "total_commissions": 1250.75,
                "pending_payout": 325.50,
                "lifetime_earnings": 3250.25,
                "next_payout_date": "2023-07-31T00:00:00Z",
                "payout_schedule": "monthly",
                "minimum_payout": 50.00
            }
        }
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v):
        return v or datetime.utcnow()
    
    @root_validator
    def calculate_lifetime_earnings(cls, values):
        """Calculate lifetime earnings and next payout date."""
        total = values.get('total_commissions', 0)
        pending = values.get('pending_payout', 0)
        values['lifetime_earnings'] = total + pending
        
        # Calculate next payout date if not set
        if not values.get('next_payout_date') and values.get('payout_schedule'):
            now = datetime.utcnow()
            schedule = values.get('payout_schedule', PayoutSchedule.MONTHLY)
            
            if schedule == PayoutSchedule.WEEKLY:
                delta = timedelta(weeks=1)
            elif schedule == PayoutSchedule.BIWEEKLY:
                delta = timedelta(weeks=2)
            elif schedule == PayoutSchedule.QUARTERLY:
                delta = timedelta(weeks=13)  # Approximate
            else:  # MONTHLY
                # Handle month boundaries
                next_month = now.month % 12 + 1
                year = now.year + (1 if next_month == 1 else 0)
                try:
                    next_date = now.replace(month=next_month, day=1, year=year)
                except ValueError:
                    # Handle invalid date (e.g., Feb 30)
                    next_date = now.replace(month=next_month, day=28, year=year)
                values['next_payout_date'] = next_date
                return values
                
            values['next_payout_date'] = now + delta
            
        return values

class AffiliatePayout(BaseModel):
    """Represents a payout to an affiliate with schedule tracking."""
    id: str = Field(..., description="Unique identifier for the payout")
    affiliate_id: str = Field(..., description="Reference to affiliate")
    amount: Decimal = Field(
        ...,
        ge=Decimal('0.01'),
        max_digits=12,
        decimal_places=2,
        description="Payout amount in the specified currency"
    )
    currency: str = Field("USD", min_length=3, max_length=3,
                        description="ISO 4217 currency code")
    status: str = Field(..., 
                       description="Status of the payout (scheduled, pending, processing, paid, failed, cancelled)")
    is_recurring: bool = Field(
        False,
        description="Whether this is part of a recurring payout schedule"
    )
    schedule_id: Optional[str] = Field(
        None,
        description="ID of the recurring schedule if applicable"
    )
    payment_method: PaymentMethod = Field(..., 
                                       description="Method used for the payout")
    reference_id: Optional[str] = Field(
        None,
        description="External reference ID from payment processor"
    )
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Any notes about the payout"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AffiliateReferral(BaseModel):
    """Tracks referrals made by an affiliate."""
    id: str = Field(..., description="Unique identifier for the referral")
    affiliate_id: str = Field(..., description="Referring affiliate")
    referred_user_id: str = Field(..., description="Referred user")
    referral_code: str = Field(..., min_length=4, max_length=20,
                             description="Code used for the referral")
    source: str = Field("direct", 
                       description="Source of the referral (e.g., 'email', 'social', 'website')")
    campaign: Optional[str] = Field(
        None,
        description="Campaign identifier, if applicable"
    )
    ip_address: Optional[str] = Field(
        None,
        description="IP address of the referred user"
    )
    user_agent: Optional[str] = Field(
        None,
        description="User agent of the referred user's browser/device"
    )
    converted: bool = Field(
        False,
        description="Whether the referral resulted in a conversion"
    )
    conversion_date: Optional[datetime] = Field(
        None,
        description="When the referral was converted"
    )
    conversion_value: Decimal = Field(
        default=Decimal('0'),
        ge=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        description="Value of the conversion in base currency"
    )
    commission_earned: Decimal = Field(
        default=Decimal('0'),
        ge=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        description="Commission earned from this referral"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AffiliateNotificationPreferences(BaseModel):
    """Notification preferences for affiliates."""
    email_commission_earned: bool = Field(
        True,
        description="Email when commission is earned"
    )
    email_payout_sent: bool = Field(
        True,
        description="Email when payout is processed"
    )
    email_monthly_statement: bool = Field(
        True,
        description="Email monthly statement"
    )
    email_promotions: bool = Field(
        True,
        description="Receive promotional emails"
    )
    email_newsletter: bool = Field(
        True,
        description="Subscribe to newsletter"
    )
    push_commission_earned: bool = Field(
        True,
        description="Push notification for new commissions"
    )
    push_payout_sent: bool = Field(
        True,
        description="Push notification for payouts"
    )
    sms_important_updates: bool = Field(
        False,
        description="SMS for important updates"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "email_commission_earned": True,
                "email_payout_sent": True,
                "email_monthly_statement": True,
                "email_promotions": False,
                "email_newsletter": True,
                "push_commission_earned": True,
                "push_payout_sent": True,
                "sms_important_updates": False
            }
        }
