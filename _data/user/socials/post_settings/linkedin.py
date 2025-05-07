from pydantic import BaseModel
from typing import Optional, List

class LinkedInSupportedFormats(BaseModel):
    supported_formats: List[str] = ["Text", "Image", "Video", "Document", "Poll"]
    supported_file_types: List[str] = ["jpg", "png", "gif", "mp4", "pdf"]

class LinkedInConfig(BaseModel):
    enabled: bool = True
    post_format: str = "Text"
    supported_formats: LinkedInSupportedFormats = LinkedInSupportedFormats()
    minimum_characters: Optional[int] = 50
    maximum_characters: int = 3000
    formatting_instructions: str = (
        "IMPORTANT: Format the post with proper line breaks for readability. "
        "Put each list item on a new line, and ensure paragraph breaks where appropriate. "
        "Add line breaks before and after lists. "
        "For LinkedIn, use emojis sparingly and maintain a professional tone."
    )
    include_hashtags: bool = True
    max_hashtags: int = 5
