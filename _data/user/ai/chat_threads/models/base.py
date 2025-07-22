"""
Base models for AI chat threads.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator
from uuid import UUID, uuid4

class MessageType(str, Enum):
    """Types of messages in a chat thread."""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    SYSTEM = "system"
    AI = "ai"

class MessageStatus(str, Enum):
    """Status of a message in the delivery lifecycle."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class ParticipantRole(str, Enum):
    """Roles of participants in a chat thread."""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"
    ADMIN = "admin"
    BOT = "bot"

class BaseModelWithTimestamps(BaseModel):
    """Base model with common timestamp fields."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None
        }
        use_enum_values = True
        validate_assignment = True

    def model_post_init(self, __context):
        """Update timestamps on model initialization."""
        self.updated_at = datetime.utcnow()
        return super().model_post_init(__context)
