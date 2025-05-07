"""
TextStats: Tracks SMS/text campaign data and analytics.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class TextStats(BaseModel):
    total_texts: int = Field(0, description="Total number of texts sent in the campaign")
    delivered: int = Field(0, description="Number of texts successfully delivered")
    failed: int = Field(0, description="Number of failed text deliveries")
    replies: int = Field(0, description="Number of replies received")
    opt_outs: int = Field(0, description="Number of recipients who opted out")
    last_text_at: Optional[str] = Field(None, description="Timestamp of the most recent text (ISO 8601)")
    message_templates: Optional[List[str]] = Field(default_factory=list, description="Templates used in the campaign")
    notes: Optional[List[str]] = Field(default_factory=list, description="Notes on text interactions")

    class Config:
        title = "TextStats"
        arbitrary_types_allowed = True
