"""
Blog Plan and Calendar Models
- Defines BlogPlan (with required/optional fields)
- Defines BlogCalendar (dynamic list of plans with status/urgency)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class BlogStatus(str, Enum):
    draft = "draft"
    scheduled = "scheduled"
    published = "published"
    needs_review = "needs_review"
    blocked = "blocked"

class BlogUrgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class BlogPlan(BaseModel):
    """
    Model for planning a single blog post.
    """
    title: str = Field(..., description="Blog plan title")
    post_type: Literal["thought", "tutorial", "case_study", "news", "announcement", "other"] = Field(..., description="Type of post")
    thoughts: Optional[str] = Field(None, description="Initial thoughts or notes for the post")
    sources: Optional[List[str]] = Field(None, description="List of source URLs or references")
    target_keywords: Optional[List[str]] = Field(None, description="Target SEO keywords")
    outline: Optional[List[str]] = Field(None, description="Outline or main points for the blog post")
    status: BlogStatus = Field(BlogStatus.draft, description="Current status of the blog plan")
    urgency: BlogUrgency = Field(BlogUrgency.medium, description="Urgency level for this blog post")
    due_date: Optional[str] = Field(None, description="Due date (ISO 8601)")
    author: Optional[str] = Field(None, description="Assigned author")
    notes: Optional[str] = Field(None, description="Additional notes or instructions")
