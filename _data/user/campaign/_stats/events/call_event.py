"""
CallEvent: Represents a single call instance for campaign analytics aggregation.
"""
from pydantic import BaseModel, Field
from typing import Optional

class CallEvent(BaseModel):
    call_id: str = Field(..., description="Unique identifier for the call")
    campaign_id: Optional[str] = Field(None, description="ID of the associated campaign")
    user_id: Optional[str] = Field(None, description="ID of the user making the call")
    lead_id: Optional[str] = Field(None, description="ID of the lead being called")
    timestamp: str = Field(..., description="Timestamp of the call (ISO 8601)")
    duration_seconds: Optional[float] = Field(None, description="Duration of the call in seconds")
    was_successful: bool = Field(False, description="Whether the call resulted in successful contact")
    was_missed: bool = Field(False, description="Whether the call was missed or not answered")
    recording_url: Optional[str] = Field(None, description="URL to the call recording")
    notes: Optional[str] = Field(None, description="Notes or summary about the call outcome")
    call_type: Optional[str] = Field(None, description="Type of call (inbound, outbound, follow-up, etc.)")
    phone_number: Optional[str] = Field(None, description="Phone number dialed or received from")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags for segmentation or analysis")
    # todo: Add fields for advanced analytics or integration as needed

    class Config:
        title = "CallEvent"
        arbitrary_types_allowed = True
