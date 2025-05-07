"""
GlobalAnalytics: Universal analytics model adaptable to any platform, with Facebook and LinkedIn defaults.
"""
from pydantic import BaseModel, Field
from typing import Dict, Optional
from config_lead_ignite._data.user.analytics.ai_actions.ai_actions import AIUsageLog
from config_lead_ignite._data.user.analytics.__init__ import AnalyticsBase, PlatformAnalytics, SocialAnalytics
from config_lead_ignite._data.user.analytics.audit_models import AuditLog, ActivityLog
from config_lead_ignite._data.user.analytics.facebook import FacebookPostAnalyticsList
from config_lead_ignite._data.user.analytics.linkedin import LinkedInPostAnalyticsList


class GlobalAnalytics(BaseModel):
    facebook: PlatformAnalytics = Field(default_factory=PlatformAnalytics, description="Facebook analytics")
    linkedin: PlatformAnalytics = Field(default_factory=PlatformAnalytics, description="LinkedIn analytics")
    other: Dict[str, PlatformAnalytics] = Field(default_factory=dict, description="Other platforms (key: platform name)")
    ai_usage: Optional[AIUsageLog] = Field(None, description="Aggregated AI usage analytics for the user")
    audit_logs: Optional[list[AuditLog]] = Field(default_factory=list, description="User audit logs")
    activity_logs: Optional[list[ActivityLog]] = Field(default_factory=list, description="User activity logs")
    facebook_post_analytics: Optional[FacebookPostAnalyticsList] = Field(None, description="Analytics for Facebook posts")
    linkedin_post_analytics: Optional[LinkedInPostAnalyticsList] = Field(None, description="Analytics for LinkedIn posts")
    social_analytics: Optional[SocialAnalytics] = Field(None, description="Aggregate analytics for all platforms")
    # todo: Add more analytics modules as needed (e.g., campaign analytics)

    class Config:
        title = "GlobalAnalytics"
        arbitrary_types_allowed = True
