"""
TextEvent: Represents a single SMS/text message event for campaign analytics aggregation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class TextEvent(BaseModel):
    event_id: str = Field(..., description="Unique identifier for the text event")
    campaign_id: Optional[str] = Field(None, description="ID of the associated campaign")
    user_id: Optional[str] = Field(None, description="ID of the user sending the text")
    lead_id: Optional[str] = Field(None, description="ID of the lead receiving the text")
    timestamp: str = Field(..., description="Timestamp of the text (ISO 8601)")
    phone_number: Optional[str] = Field(None, description="Phone number texted")
    status: Optional[str] = Field(None, description="Delivery status (delivered, failed, etc.)")
    message: str = Field(..., description="Text message content")
    template_id: Optional[str] = Field(None, description="ID of the message template used")
    was_reply: bool = Field(False, description="Whether this message was a reply")
    opt_out: bool = Field(False, description="Whether the recipient opted out")
    media_urls: Optional[List[str]] = Field(default_factory=list, description="Media URLs attached to the message")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for segmentation or analysis")
    # todo: Add more analytics fields as needed

    class Config:
        title = "TextEvent"
        arbitrary_types_allowed = True
