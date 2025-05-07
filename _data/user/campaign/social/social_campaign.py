"""
SocialCampaign: Model for managing and aggregating social media campaigns.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from config_lead_ignite._data.user.campaign._stats.social_stats import SocialStats
from config_lead_ignite._data.user.campaign._stats.events.social_event import SocialEvent

if TYPE_CHECKING:
    from config_lead_ignite._data.user.campaign._leads.real_estate.mls_lead import MLSRealEstateLead

class SocialCampaign(BaseModel):
    campaign_id: str = Field(..., description="Unique identifier for the social campaign")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    stats: SocialStats = Field(default_factory=SocialStats, description="Aggregated social stats")
    events: List[SocialEvent] = Field(default_factory=list, description="List of social events (posts/interactions)")
    start_date: Optional[str] = Field(None, description="Campaign start date (ISO 8601)")
    end_date: Optional[str] = Field(None, description="Campaign end date (ISO 8601)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for segmentation or analysis")
    leads: Optional[List["MLSRealEstateLead"]] = Field(default_factory=list, description="Leads associated with this social campaign (e.g., MLS real estate leads)")
    # todo: Add fields for campaign owner, platform, etc.

    class Config:
        title = "SocialCampaign"
        arbitrary_types_allowed = True
