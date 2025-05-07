from pydantic import BaseModel, Field
from typing import Optional

class SocialLinks(BaseModel):
    """All social media/profile links."""
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    twitter: Optional[str] = Field(None, description="Twitter/X handle")
    medium: Optional[str] = Field(None, description="Medium username or URL")
