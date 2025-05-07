"""
SocialEvent: Represents a single social post or interaction for campaign analytics aggregation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class SocialEvent(BaseModel):
    event_id: str = Field(..., description="Unique identifier for the social event")
    campaign_id: Optional[str] = Field(None, description="ID of the associated campaign")
    user_id: Optional[str] = Field(None, description="ID of the user posting or interacting")
    platform: Optional[str] = Field(None, description="Social platform (e.g., Facebook, LinkedIn, Twitter)")
    post_id: Optional[str] = Field(None, description="ID of the post or comment")
    event_type: str = Field(..., description="Type of event (post, comment, like, share, etc.)")
    timestamp: str = Field(..., description="Timestamp of the event (ISO 8601)")
    content: Optional[str] = Field(None, description="Content of the post or comment")
    url: Optional[str] = Field(None, description="URL to the post or event")
    media_urls: Optional[List[str]] = Field(default_factory=list, description="List of media URLs attached")
    likes: Optional[int] = Field(0, description="Number of likes or reactions")
    comments: Optional[int] = Field(0, description="Number of comments")
    shares: Optional[int] = Field(0, description="Number of shares or reposts")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags or hashtags")
    # todo: Add more analytics fields as needed

    class Config:
        title = "SocialEvent"
        arbitrary_types_allowed = True
