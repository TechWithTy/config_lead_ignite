"""
Message models for AI chat threads.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import Field, HttpUrl, field_validator
from uuid import UUID

from .base import BaseModelWithTimestamps, MessageType, MessageStatus

class Attachment(BaseModelWithTimestamps):
    """Represents a file or media attachment in a message."""
    url: HttpUrl = Field(..., description="URL to the attached file")
    name: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type of the file")
    size: int = Field(..., description="File size in bytes")
    width: Optional[int] = Field(None, description="Width in pixels (for images/videos)")
    height: Optional[int] = Field(None, description="Height in pixels (for images/videos)")
    duration: Optional[float] = Field(None, description="Duration in seconds (for audio/video)")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="URL to a thumbnail preview")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MessageContent(BaseModelWithTimestamps):
    """Base class for message content."""
    text: Optional[str] = Field(None, description="Text content of the message")
    html: Optional[str] = Field(None, description="HTML formatted content")
    markdown: Optional[str] = Field(None, description="Markdown formatted content")

class Message(BaseModelWithTimestamps):
    """Represents a message in a chat thread."""
    thread_id: UUID = Field(..., description="ID of the thread containing this message")
    sender_id: UUID = Field(..., description="ID of the user/AI who sent the message")
    sender_type: str = Field(..., description="Type of the sender (user/ai/system)")
    content: MessageContent = Field(..., description="Message content")
    message_type: MessageType = Field(MessageType.TEXT, description="Type of the message")
    status: MessageStatus = Field(MessageStatus.PENDING, description="Delivery status")
    reply_to: Optional[UUID] = Field(None, description="ID of the message this is a reply to")
    attachments: List[Attachment] = Field(default_factory=list, description="Attached files/media")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator('sender_type')
    def validate_sender_type(cls, v):
        valid_types = ['user', 'ai', 'system', 'bot']
        if v not in valid_types:
            raise ValueError(f"sender_type must be one of {valid_types}")
        return v

    def add_attachment(self, attachment: Attachment) -> None:
        """Add an attachment to the message."""
        self.attachments.append(attachment)
        self.updated_at = datetime.utcnow()

    def update_status(self, status: MessageStatus) -> None:
        """Update the message status."""
        self.status = status
        self.updated_at = datetime.utcnow()

class MessageUpdate(BaseModelWithTimestamps):
    """Model for updating a message."""
    content: Optional[MessageContent] = None
    status: Optional[MessageStatus] = None
    metadata: Optional[Dict[str, Any]] = None
