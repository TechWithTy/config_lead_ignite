from pydantic import BaseModel
from typing import Optional
from typing import List

class SupportedFormats(BaseModel):
    supported_formats: List[str] = ["Text", "Image", "Video"]
    supported_file_types: List[str] = ["jpg", "png", "gif", "mp4"]

class SocialConfig(BaseModel):
    enabled: bool = True
    post_format: str = "Text"
    supported_formats: SupportedFormats     
    minimum_characters: Optional[int] = 1500
    maximum_characters: int = 2000
    formatting_instructions: str = (
        "IMPORTANT: Format the post with proper line breaks for readability. "
        "Put each list item on a new line, and ensure paragraph breaks where appropriate. "
        "Add line breaks before and after lists."
    )