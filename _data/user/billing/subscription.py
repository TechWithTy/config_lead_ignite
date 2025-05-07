"""
Subscription and CreditUsage models for user subscription and credit tracking.
"""
from pydantic import BaseModel, Field, conint
from typing import Optional, List, Dict
from .plan import PlanDetails

class CreditUsage(BaseModel):
    """Tracks user credit usage for API, posts, analytics, etc."""
    total_credits: conint(ge=0) = Field(0, description="Total credits available")
    used_credits: conint(ge=0) = Field(0, description="Credits used so far")
    last_reset: Optional[str] = Field(None, description="Last time credits were reset (ISO 8601)")
    usage_history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="History of credit usage events")


class Subscription(BaseModel):
    """Tracks user subscription status, plan details, and renewal info."""
    plan: PlanDetails = Field(..., description="Detailed plan configuration for this subscription")
    is_active: bool = Field(True, description="Is the subscription currently active?")
    end_date: Optional[str] = Field(None, description="Subscription end date (ISO 8601)")
    auto_renew: bool = Field(True, description="Will the subscription auto-renew?")
