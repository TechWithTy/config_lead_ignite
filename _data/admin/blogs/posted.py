"""
PostedBlog model for tracking published blog content and cross-platform social posting.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from config._data.user.post_settings.main import SocialConfig

class PostType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    data = "data"
    link = "link"
    other = "other"

class SocialPlatform(str, Enum):
    linkedin = "linkedin"
    twitter = "twitter"
    facebook = "facebook"
    instagram = "instagram"
    threads = "threads"
    mastodon = "mastodon"
    bluesky = "bluesky"
    tiktok = "tiktok"
    youtube = "youtube"
    medium = "medium"
    devto = "devto"
    custom = "custom"

class SocialPostMeta(BaseModel):
    platform: SocialPlatform
    post_id: Optional[str] = Field(None, description="Platform-specific post ID")
    url: Optional[str] = Field(None, description="URL to the posted content")
    text: Optional[str] = Field(None, description="Text content of the post")
    media: Optional[str] = Field(None, description="Media in the post")
    posted_at: Optional[str] = Field(None, description="Timestamp posted (ISO 8601)")
    status: Optional[str] = Field(None, description="Status/result of posting")
    social_config: Optional[SocialConfig] = Field(None, description="Social config")

class PostedBlog(BaseModel):
    """
    Represents a blog that has been posted, including core blog data and cross-platform posting info.
    """
    blog_id: str = Field(..., description="Unique blog identifier")
    title: str = Field(..., description="Blog post title")
    author: str = Field(..., description="Author name or ID")
    summary: Optional[str] = Field(None, description="Summary or excerpt")
    content: Optional[str] = Field(None, description="Full or partial blog content")
    post_type: PostType = Field(..., description="Type of post: text, image, etc.")
    tags: Optional[List[str]] = Field(None, description="Tags or keywords")
    published_at: Optional[str] = Field(None, description="Original publish date (ISO 8601)")
    canonical_url: Optional[str] = Field(None, description="Canonical blog URL")
    social_posts: List[SocialPostMeta] = Field(default_factory=list, description="List of social platforms this blog was posted to")
    extra_data: Optional[dict] = Field(default_factory=dict, description="Any extra metadata (e.g. analytics, reactions)")
