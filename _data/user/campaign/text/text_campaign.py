"""
TextCampaign: Model for managing and aggregating SMS/text campaigns.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from config_lead_ignite._data.user.campaign._stats.text_stats import TextStats
from config_lead_ignite._data.user.campaign._stats.events.text_event import TextEvent

if TYPE_CHECKING:
    from config_lead_ignite._data.user.campaign._leads.real_estate.mls_lead import MLSRealEstateLead

class TextCampaign(BaseModel):
    campaign_id: str = Field(..., description="Unique identifier for the text campaign")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    stats: TextStats = Field(default_factory=TextStats, description="Aggregated text stats")
    events: List[TextEvent] = Field(default_factory=list, description="List of text message events")
    start_date: Optional[str] = Field(None, description="Campaign start date (ISO 8601)")
    end_date: Optional[str] = Field(None, description="Campaign end date (ISO 8601)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for segmentation or analysis")
    leads: Optional[List["MLSRealEstateLead"]] = Field(default_factory=list, description="Leads associated with this text campaign (e.g., MLS real estate leads)")
    # todo: Add fields for campaign owner, recipient list, etc.

    class Config:
        title = "TextCampaign"
        arbitrary_types_allowed = True
