from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class SubscriptionType(str, Enum):
    monthly = "monthly"
    yearly = "yearly"

class SubscriptionStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class UserProfileSubscription(BaseModel):
    id: str = Field(..., description="Unique subscription record ID")
    user_id: str = Field(..., description="User ID")
    stripe_subscription_id: str = Field(..., description="Stripe subscription ID")
    name: str = Field(..., description="Subscription plan name")
    type: SubscriptionType = Field(..., description="Subscription type (monthly/yearly)")
    status: SubscriptionStatus = Field(..., description="Subscription status (active/inactive)")
    price: str = Field(..., description="Subscription price")
    renewal_date: Optional[str] = Field(None, description="Next renewal date (ISO 8601)")
    plan_details: Optional[str] = Field(None, description="Additional plan details as JSON string or description")
