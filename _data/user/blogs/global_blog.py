"""
GlobalBlog: Aggregates planned and posted blogs for unified blog management.
"""
from pydantic import BaseModel, Field
from typing import List
from .plan import BlogPlan
from .posted import PostedBlog
from .content import BlogContent

class GlobalBlog(BaseModel):
    blogs_planned: List[BlogPlan] = Field(default_factory=list, description="Planned blog posts")
    blogs_posted: List[PostedBlog] = Field(default_factory=list, description="Posted blog content")
    blogs_content: List[BlogContent] = Field(default_factory=list, description="Blog content")
    # todo: Add fields for blog calendar, categories, SEO metadata, etc.

    class Config:
        title = "GlobalBlog"
        arbitrary_types_allowed = True
