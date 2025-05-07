"""
PlanOption model for user subscription plans.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class PlanOption(str, Enum):
    free = "free"
    pro = "pro"
    business = "business"
    enterprise = "enterprise"

class RenewalInterval(str, Enum):
    monthly = "monthly"
    yearly = "yearly"
    quarterly = "quarterly"

class PlanCredits(BaseModel):
    """Credit allocations per category for a plan."""
    generation: int = Field(0, description="Credits for content/post generation")
    nurture: int = Field(0, description="Credits for nurture/engagement actions")
    analytics: int = Field(0, description="Credits for analytics/reporting")
    research: int = Field(0, description="Credits for research")
    other: int = Field(0, description="Credits for other AI actions")

class PlanDetails(BaseModel):
    """Details for a marketing AI bot subscription plan, including credits and renewal info."""
    name: PlanOption = Field(..., description="Plan tier")
    credits: PlanCredits = Field(default_factory=PlanCredits, description="Credit allocations for this plan")
    start_date: Optional[str] = Field(None, description="Plan start date (ISO 8601)")
    renewal_date: Optional[str] = Field(None, description="Next renewal date (ISO 8601)")
    interval: RenewalInterval = Field(RenewalInterval.monthly, description="Renewal interval for the plan")
    description: Optional[str] = Field(None, description="Plan description or notes")
