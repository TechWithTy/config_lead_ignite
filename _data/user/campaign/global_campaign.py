"""
GlobalCampaign: Aggregates all campaign types and provides a unified interface for campaign management.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from .campaign_base import CampaignBase
from .call.call_campaign import CallCampaign
from .social.social_campaign import SocialCampaign
from .text.text_campaign import TextCampaign

class GlobalCampaign(BaseModel):
    campaigns: List[CampaignBase] = Field(default_factory=list, description="All campaigns (generic base)")
    call_campaigns: List[CallCampaign] = Field(default_factory=list, description="All call campaigns")
    social_campaigns: List[SocialCampaign] = Field(default_factory=list, description="All social campaigns")
    text_campaigns: List[TextCampaign] = Field(default_factory=list, description="All text campaigns")
    last_updated: Optional[str] = Field(None, description="Timestamp of last campaign update (ISO 8601)")
    # todo: Add fields for campaign analytics, segmentation, or cross-channel orchestration

    class Config:
        title = "GlobalCampaign"
        arbitrary_types_allowed = True
