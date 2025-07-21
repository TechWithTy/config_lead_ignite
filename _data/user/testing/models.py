"""
Models for beta testers and pilot testers in the application.

This module provides models for managing beta and pilot testers, leveraging core user models
to avoid type duplication and maintain consistency across the application.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Import core models to avoid duplication
from ..core import CompanyInfo, PII, ContactInfo, LocationInfo

class TesterType(str, Enum):
    """Type of tester (beta or pilot)."""
    BETA = "beta"
    PILOT = "pilot"

class ICPType(str, Enum):
    """Ideal Customer Profile types."""
    GROWTH_FOCUSED_WHOLESALER = "growth_focused_wholesaler"
    SYSTEMATIZING_FLIPPER_INVESTOR = "systematizing_flipper_investor"
    SAVVY_CRE_DEALMAKER = "savvy_cre_dealmaker"
    SCALING_RE_AGENT = "scaling_real_estate_agent"

class EmployeeCount(str, Enum):
    """Employee count ranges."""
    JUST_ME = "1"
    TWO_TO_FIVE = "2_5"
    SIX_TO_TEN = "6_10"
    ELEVEN_TO_TWENTY_FIVE = "11_25"
    TWENTY_SIX_TO_FIFTY = "26_50"
    FIFTY_ONE_PLUS = "51_plus"

class DealsClosed(str, Enum):
    """Number of deals closed ranges."""
    ZERO_TO_FIVE = "0_5"
    SIX_TO_TEN = "6_10"
    ELEVEN_TO_TWENTY = "11_20"
    TWENTY_ONE_TO_FIFTY = "21_50"
    FIFTY_ONE_PLUS = "51_plus"

class PainPoint(str, Enum):
    """Common pain points for testers."""
    INCONSISTENT_DEAL_FLOW = "inconsistent_deal_flow"
    TOO_MUCH_TIME_PROSPECTING = "too_much_time_prospecting"
    LEADS_GO_COLD = "leads_go_cold"
    LOW_CONVERSION_RATE = "low_conversion_rate"
    DIFFICULTY_SCALING = "difficulty_scaling"
    HIGH_LEAD_GEN_COSTS = "high_lead_generation_costs"
    MISSING_OFF_MARKET_DEALS = "missing_off_market_deals"

class TesterStatus(str, Enum):
    """Status of the tester's application/participation."""
    APPLIED = "applied"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    REJECTED = "rejected"

class BaseTester(BaseModel):
    """Base model for all tester types.
    
    This model references core user models to avoid duplicating user information.
    """
    user_id: str = Field(..., description="Reference to core user ID")
    tester_type: TesterType
    status: TesterStatus = Field(TesterStatus.APPLIED, description="Current status of the tester")
    applied_at: datetime = Field(default_factory=datetime.utcnow, description="When the application was submitted")
    approved_at: Optional[datetime] = Field(None, description="When the application was approved")
    started_at: Optional[datetime] = Field(None, description="When the testing period started")
    completed_at: Optional[datetime] = Field(None, description="When testing was completed")
    notes: Optional[str] = Field(None, description="Internal notes about the tester")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Reference to core user models - these will be populated from the user's profile
    pii: Optional[PII] = Field(None, description="User's PII (from core profile)")
    contact: Optional[ContactInfo] = Field(None, description="User's contact info (from core profile)")
    location: Optional[LocationInfo] = Field(None, description="User's location info (from core profile)")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class BetaTester(BaseTester):
    """Model for beta testers with specific fields from the beta tester form.
    
    Extends BaseTester with beta-specific fields while leveraging core user models
    for common user information.
    """
    tester_type: TesterType = Field(TesterType.BETA, const=True)
    
    # Company information - references core CompanyInfo model
    company: CompanyInfo = Field(..., description="Company information")
    
    # Beta-specific fields
    icp_type: ICPType = Field(..., description="Ideal customer profile type")
    employee_count: EmployeeCount = Field(..., description="Number of employees")
    deals_closed_last_year: DealsClosed = Field(..., description="Number of deals closed last year")
    pain_points: List[PainPoint] = Field(..., description="Selected pain points")
    wanted_features: List[str] = Field(..., description="IDs of features the tester is interested in")
    feature_votes: List[str] = Field(default_factory=list, description="IDs of features the tester has voted on")
    deal_documents: List[str] = Field(default_factory=list, description="URLs to deal documents (HUDs, etc.)")
    terms_accepted: bool = Field(False, description="Whether terms were accepted")

class PilotTester(BetaTester):
    """Model for pilot testers with additional fields specific to pilot program.
    
    Extends BetaTester with additional pilot-specific fields while maintaining
    all the beta tester functionality.
    """
    tester_type: TesterType = Field(TesterType.PILOT, const=True)
    
    # Pilot-specific fields
    team_size_acquisitions: str = Field(..., description="Number of people focused on acquisitions")
    primary_deal_sources: List[str] = Field(..., description="Primary sources for deals")
    current_crm: Optional[str] = Field(None, description="Current CRM or lead management tool")
    interested_features: List[str] = Field(..., description="Pilot features of interest")
    success_metrics: str = Field(..., description="What success would look like for the tester")
    feedback_commitment: bool = Field(False, description="Agreed to provide feedback")
    payment_agreement: bool = Field(False, description="Acknowledged payment step")

class TesterResponse(BaseModel):
    """Response model for tester operations."""
    success: bool
    message: str
    tester: Optional[BaseTester] = None

class TesterListResponse(BaseModel):
    """Response model for listing testers."""
    count: int
    testers: List[BaseTester]
