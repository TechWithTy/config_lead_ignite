from pydantic import BaseModel, Field
from typing import Optional

class SavedSearch(BaseModel):
    name: str = Field(..., description="Name of the saved search")
    query: str = Field(..., description="Query string or filter for the saved search")
    created_at: Optional[str] = Field(None, description="Timestamp when saved search was created (ISO 8601)")
    last_used_at: Optional[str] = Field(None, description="Timestamp when search was last used (ISO 8601)")
    # todo: Add owner, tags, and sharing fields as needed
