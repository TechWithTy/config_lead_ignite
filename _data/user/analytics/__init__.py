"""
Dynamic analytics models for social media platforms. 
- AnalyticsBase: core metrics
- PlatformAnalytics: stackable analytics for each platform
- SocialAnalytics: aggregate analytics for insights/automation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum

class EngagementType(str, Enum):
    like = "like"
    comment = "comment"
    share = "share"
    view = "view"
    click = "click"
    save = "save"
    repost = "repost"
    impression = "impression"
    follow = "follow"
    mention = "mention"
    reaction = "reaction"
    other = "other"

class AnalyticsBase(BaseModel):
    """Base model for analytics, reusable across platforms."""
    post_id: Optional[str] = Field(None, description="Unique post identifier")
    timestamp: Optional[str] = Field(None, description="Event timestamp (ISO 8601)")
    reach: Optional[int] = Field(None, description="How many users saw the post")
    impressions: Optional[int] = Field(None, description="Number of times post was shown")
    engagement: Optional[int] = Field(None, description="Total engagement count")
    engagement_rate: Optional[float] = Field(None, description="Engagement rate (0-1)")
    clicks: Optional[int] = Field(None, description="Number of link or media clicks")
    ctr: Optional[float] = Field(None, description="Click-through rate (0-1)")
    saves: Optional[int] = Field(None, description="Number of saves/bookmarks")
    shares: Optional[int] = Field(None, description="Number of shares/reposts")
    comments: Optional[int] = Field(None, description="Number of comments")
    likes: Optional[int] = Field(None, description="Number of likes/reactions")
    followers_gained: Optional[int] = Field(None, description="Followers gained from post")
    sentiment: Optional[float] = Field(None, description="Sentiment score (-1 to 1)")
    virality_score: Optional[float] = Field(None, description="Custom virality metric")
    extra: Optional[Dict[str, float]] = Field(default_factory=dict, description="Other custom metrics")

class PostAnalyticsList(BaseModel):
    """
    Generic list of post analytics for any platform, with aggregation.
    """
    posts: list[AnalyticsBase] = Field(default_factory=list, description="List of post analytics (any platform)")
    summary: Optional[dict] = Field(default_factory=dict, description="Aggregated metrics or insights for all posts")

class PlatformAnalytics(BaseModel):
    """Stackable analytics for a single platform."""
    platform: str = Field(..., description="Social media platform name")
    analytics: List[AnalyticsBase] = Field(default_factory=list, description="Analytics events for this platform")
    summary: Optional[Dict[str, float]] = Field(default_factory=dict, description="Summarized analytics (e.g. avg, totals)")

class SocialAnalytics(BaseModel):
    """Aggregate analytics for all platforms, for insights and automation."""
    user_id: Optional[str] = Field(None, description="User or account ID")
    platforms: List[PlatformAnalytics] = Field(default_factory=list, description="Analytics for each platform")
    global_summary: Optional[Dict[str, float]] = Field(default_factory=dict, description="Global analytics summary")

    def add_platform_analytics(self, platform_analytics: PlatformAnalytics):
        self.platforms.append(platform_analytics)

    def get_platform(self, platform: str) -> Optional[PlatformAnalytics]:
        for p in self.platforms:
            if p.platform == platform:
                return p
        return None

    def aggregate(self):
        """Aggregate analytics across all platforms for high-level insights."""
        total_engagement = sum(
            sum(a.engagement or 0 for a in p.analytics) for p in self.platforms
        )
        total_impressions = sum(
            sum(a.impressions or 0 for a in p.analytics) for p in self.platforms
        )
        self.global_summary = {
            "total_engagement": total_engagement,
            "total_impressions": total_impressions,
            "platform_count": len(self.platforms),
        }
