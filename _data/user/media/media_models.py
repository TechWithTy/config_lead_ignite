"""
Media Models
------------
Global media object with CDN support for user-uploaded or referenced media assets.
Follows DRY, type-safe, and extensible design for integration with cloud/CDN providers.
"""
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, HttpUrl

class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"

class CDNProvider(str, Enum):
    CLOUDINARY = "cloudinary"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    CUSTOM = "custom"
    NONE = "none"  # For local or direct links

class MediaAsset(BaseModel):
    id: str  # Unique media identifier
    type: MediaType
    url: HttpUrl  # Direct or CDN URL
    cdn_provider: CDNProvider = CDNProvider.NONE
    cdn_meta: Optional[Dict[str, str]] = None  # Extra CDN-specific info
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # For video/audio
    content_type: Optional[str] = None  # MIME type
    # ! Ensure all URLs are validated and safe for public use

    class Config:
        schema_extra = {
            "example": {
                "id": "media_12345",
                "type": "image",
                "url": "https://cdn.example.com/media_12345.jpg",
                "cdn_provider": "cloudinary",
                "cdn_meta": {"resource_type": "image", "format": "jpg"},
                "alt_text": "User profile picture",
                "width": 512,
                "height": 512,
                "content_type": "image/jpeg"
            }
        }

# * Usage:
# Use MediaAsset as a field in any model that references media (profile, post, etc.)
# Supports extensible CDN integration and metadata for analytics, security, and optimization.
