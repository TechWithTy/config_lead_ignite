"""
GlobalBilling: Aggregates all billing, credit, plan, and subscription models for unified user billing tracking.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from .billing_history import BillingHistoryItem
from .billing import BillingInfo, PaymentInfo
from .credit_models import AICredits, LeadCredits, SkipTraceCredits
from .plan import PlanDetails
from .subscription_models import UserProfileSubscription
from .subscription import Subscription, CreditUsage

class GlobalBilling(BaseModel):
    billing_info: Optional[BillingInfo] = Field(None, description="User's billing address and payment info")
    payment_methods: Optional[List[PaymentInfo]] = Field(default_factory=list, description="All user payment methods")
    billing_history: Optional[List[BillingHistoryItem]] = Field(default_factory=list, description="User's full billing history")
    ai_credits: Optional[AICredits] = Field(None, description="AI credits for the user")
    lead_credits: Optional[LeadCredits] = Field(None, description="Lead credits for the user")
    skip_trace_credits: Optional[SkipTraceCredits] = Field(None, description="Skip trace credits for the user")
    plan_details: Optional[PlanDetails] = Field(None, description="Current plan details")
    subscription: Optional[Subscription] = Field(None, description="Active subscription object")
    user_profile_subscription: Optional[UserProfileSubscription] = Field(None, description="Legacy or external subscription record")
    credit_usage: Optional[CreditUsage] = Field(None, description="Aggregated credit usage tracking")

    class Config:
        title = "GlobalBilling"
        arbitrary_types_allowed = True
