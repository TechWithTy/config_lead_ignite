"""
GlobalResearchStats: Aggregates topic research results and analytics for a user or organization.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from . import TopicResearchResult

class GlobalResearchStats(BaseModel):
    topics: List[TopicResearchResult] = Field(default_factory=list, description="All topic research results")
    total_topics: int = Field(0, description="Total number of researched topics")
    last_researched_at: Optional[str] = Field(None, description="Timestamp of the most recent research event (ISO 8601)")
    research_tags: Optional[List[str]] = Field(default_factory=list, description="Tags for research segmentation or filtering")
    # todo: Add fields for research analytics, user engagement, or source breakdowns as needed

    class Config:
        title = "GlobalResearchStats"
        arbitrary_types_allowed = True
