"""
CallCampaign: Model for managing and aggregating call campaigns.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from config_lead_ignite._data.user.campaign._stats.call_stats import CallStats
from config_lead_ignite._data.user.campaign._stats.events.call_event import CallEvent

if TYPE_CHECKING:
    from config_lead_ignite._data.user.campaign.leads.real_estate.mls_lead import MLSRealEstateLead

class CallCampaign(BaseModel):
    campaign_id: str = Field(..., description="Unique identifier for the call campaign")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    stats: CallStats = Field(default_factory=CallStats, description="Aggregated call stats")
    events: List[CallEvent] = Field(default_factory=list, description="List of call events")
    start_date: Optional[str] = Field(None, description="Campaign start date (ISO 8601)")
    end_date: Optional[str] = Field(None, description="Campaign end date (ISO 8601)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for segmentation or analysis")
    leads: Optional[List["MLSRealEstateLead"]] = Field(default_factory=list, description="Leads associated with this call campaign (e.g., MLS real estate leads)")
    # todo: Add fields for campaign owner, lead scoring, etc.

    class Config:
        title = "CallCampaign"
        arbitrary_types_allowed = True
