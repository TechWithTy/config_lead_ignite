"""
SocialStats: Tracks social media campaign data and analytics.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class SocialStats(BaseModel):
    total_posts: int = Field(0, description="Total number of social posts in the campaign")
    likes: int = Field(0, description="Total likes received")
    comments: int = Field(0, description="Total comments received")
    shares: int = Field(0, description="Total shares or reposts")
    reach: Optional[int] = Field(None, description="Total reach or impressions")
    engagement_rate: Optional[float] = Field(None, description="Engagement rate for posts")
    top_post_url: Optional[str] = Field(None, description="URL of the top performing post")
    last_post_at: Optional[str] = Field(None, description="Timestamp of the most recent post (ISO 8601)")
    hashtags: Optional[List[str]] = Field(default_factory=list, description="Hashtags used in the campaign")

    class Config:
        title = "SocialStats"
        arbitrary_types_allowed = True
