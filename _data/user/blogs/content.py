"""
BlogContent: Model for storing all information needed for a published blog post.
Optimized for SEO and content management.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class BlogContentStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"
    deleted = "deleted"
    scheduled = "scheduled"
    researching = "researching"

class BlogContent(BaseModel):
    title: str = Field(..., description="Blog post title (H1)")
    slug: str = Field(..., description="SEO-friendly URL slug")
    author: Optional[str] = Field(None, description="Author name or ID")
    summary: Optional[str] = Field(None, description="Short summary/description for meta tags and previews")
    content: str = Field(..., description="Full HTML/Markdown content of the blog post")
    tags: List[str] = Field(default_factory=list, description="List of topic tags (for SEO and discovery)")
    keywords: List[str] = Field(default_factory=list, description="SEO keywords for meta tags")
    status: BlogContentStatus = Field(BlogContentStatus.draft, description="Publication status")
    featured_image: Optional[str] = Field(None, description="URL of the featured image")
    canonical_url: Optional[str] = Field(None, description="Canonical URL for SEO")
    publish_date: Optional[str] = Field(None, description="Publish date (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Last updated timestamp (ISO 8601)")
    reading_time_minutes: Optional[int] = Field(None, description="Estimated reading time in minutes")
    schema_markup: Optional[dict] = Field(None, description="JSON-LD or schema.org markup for SEO")
    og_title: Optional[str] = Field(None, description="Open Graph title for social sharing")
    og_description: Optional[str] = Field(None, description="Open Graph description for social sharing")
    og_image: Optional[str] = Field(None, description="Open Graph image URL for social sharing")
    # todo: Add support for multi-author, localization, and versioning if needed
    co_authors: Optional[List[str]] = Field(None, description="List of co-author names or IDs")
    locale: Optional[str] = Field(None, description="Locale/language code (e.g., en-US, fr-FR)")
    version: Optional[int] = Field(None, description="Version number of the blog post")
    previous_versions: Optional[List[dict]] = Field(default_factory=list, description="History of previous versions (metadata or diffs)")

    class Config:
        title = "BlogContent"
        arbitrary_types_allowed = True
