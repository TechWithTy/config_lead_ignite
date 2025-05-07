"""
CampaignBase: Abstract base class for all campaign types.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class CampaignBase(BaseModel):
    campaign_id: str = Field(..., description="Unique identifier for the campaign")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    owner_id: Optional[str] = Field(None, description="User ID of the campaign owner")
    recipients: Optional[List[str]] = Field(default_factory=list, description="List of recipient user IDs or contact info (emails, phones, socials)")
    platform: Optional[str] = Field(None, description="Platform or channel for the campaign (e.g., call, sms, facebook, email, etc.)")
    leads: Optional[list] = Field(default_factory=list, description="Leads associated with this campaign (can be specialized per campaign type)")
    start_date: Optional[str] = Field(None, description="Campaign start date (ISO 8601)")
    end_date: Optional[str] = Field(None, description="Campaign end date (ISO 8601)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for segmentation or analysis")
    status: Optional[str] = Field("draft", description="Campaign status (draft, active, completed, etc.)")
    audit_log: Optional[List[dict]] = Field(default_factory=list, description="Audit log entries for campaign changes/events")
    segmentation: Optional[List[str]] = Field(default_factory=list, description="Segmentation labels or audience groups")
    external_integrations: Optional[List[str]] = Field(default_factory=list, description="IDs or names of external integrations/services")
    created_at: Optional[str] = Field(None, description="Creation timestamp (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Last updated timestamp (ISO 8601)")
    # ! Important: Extend this base for all campaign types to ensure DRY, scalable, and analytics-ready campaign modeling.

    class Config:
        title = "CampaignBase"
        arbitrary_types_allowed = True
