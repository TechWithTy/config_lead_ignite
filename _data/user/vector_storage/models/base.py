from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class VectorBaseModel(BaseModel):
    """Base model for all vector storage models"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False)
    
    class Config:
        orm_mode = True
        json_encoders = {
            UUID: str
        }
