"""
CallStats: Tracks call-related campaign data and analytics.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from .events.call_event import CallEvent

class CallStats(BaseModel):
    total_calls: int = Field(0, description="Total number of calls made in the campaign")
    successful_calls: int = Field(0, description="Number of calls resulting in successful contact")
    missed_calls: int = Field(0, description="Number of missed or unanswered calls")
    average_call_duration: Optional[float] = Field(None, description="Average call duration in seconds")
    call_recordings: Optional[List[str]] = Field(default_factory=list, description="URLs to call recordings")
    notes: Optional[List[str]] = Field(default_factory=list, description="Notes from calls")
    last_call_at: Optional[str] = Field(None, description="Timestamp of the most recent call (ISO 8601)")
    events: Optional[List[CallEvent]] = Field(default_factory=list, description="List of individual call events")

    class Config:
        title = "CallStats"
        arbitrary_types_allowed = True
