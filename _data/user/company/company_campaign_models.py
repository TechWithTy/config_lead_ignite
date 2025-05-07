from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class CampaignType(str, Enum):
    email = "email"
    text = "text"
    call = "call"
    social = "social"

class CampaignStatus(str, Enum):
    delivered = "delivered"
    delivering = "delivering"
    failed = "failed"
    pending = "pending"
    completed = "completed"
    missed = "missed"
    queued = "queued"
    read = "read"
    unread = "unread"

class CompanyCampaignsUserProfile(BaseModel):
    id: str = Field(..., description="Unique company campaigns user profile ID")
    user_id: str = Field(..., description="User ID associated with campaigns")

class CampaignAnalytics(BaseModel):
    id: str = Field(..., description="Unique campaign analytics record ID")
    user_id: str = Field(..., description="User ID")
    campaign_id: str = Field(..., description="Campaign ID")
    type: CampaignType = Field(..., description="Type of campaign")
    delivered_count: int = Field(..., description="Number of messages delivered")
    opened_count: int = Field(..., description="Number of messages opened")
    bounced_count: int = Field(..., description="Number of messages bounced")
    failed_count: int = Field(..., description="Number of messages failed")
    company_info_id: Optional[str] = Field(None, description="Associated CompanyInfo ID")

class SocialAction(BaseModel):
    id: str = Field(..., description="Unique social action ID")
    status: CampaignStatus = Field(..., description="Status of the social action")
    attempt: int = Field(..., description="Attempt number")
    successful: int = Field(..., description="Number of successful actions")
    failed: int = Field(..., description="Number of failed actions")
    view_link: str = Field(..., description="URL to view the post/action")
    type: str = Field(..., description="Type of social action (Twitter, LinkedIn, etc.)")
    reply_message: Optional[str] = Field(None, description="Reply message content")
