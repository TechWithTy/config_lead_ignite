"""
A2A (Agent-to-Agent) Protocol Models

This module defines the core data models for the A2A protocol, which enables
interoperability between different AI agents.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, validator

class MessageType(str, Enum):
    """Types of messages in the A2A protocol."""
    TASK = "task"
    MESSAGE = "message"
    ARTIFACT = "artifact"
    STATUS_UPDATE = "status_update"
    CAPABILITY_DISCOVERY = "capability_discovery"

class TaskStatus(str, Enum):
    """Status of an A2A task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ContentType(str, Enum):
    """Supported content types for message parts."""
    TEXT = "text/plain"
    JSON = "application/json"
    MARKDOWN = "text/markdown"
    HTML = "text/html"
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"
    AUDIO_MP3 = "audio/mp3"
    VIDEO_MP4 = "video/mp4"
    PDF = "application/pdf"

class MessagePart(BaseModel):
    """A single part of an A2A message with content and metadata."""
    content_type: ContentType = Field(..., description="MIME type of the content")
    content: Union[str, bytes, Dict[str, Any]] = Field(..., description="The actual content")
    name: Optional[str] = Field(None, description="Name or identifier for this part")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AgentCapability(BaseModel):
    """Describes a capability of an A2A agent."""
    name: str = Field(..., description="Name of the capability")
    description: str = Field(..., description="Description of what the capability does")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for input parameters")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for output data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AgentCard(BaseModel):
    """Metadata about an A2A agent that describes its capabilities."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human-readable name of the agent")
    description: str = Field(..., description="Description of the agent's purpose")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="List of capabilities")
    version: str = Field("1.0.0", description="Version of the agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class Task(BaseModel):
    """Represents a task in the A2A protocol."""
    task_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the task")
    parent_task_id: Optional[UUID] = Field(None, description="ID of the parent task, if any")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current status of the task")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the task was created")
    updated_at: Optional[datetime] = Field(None, description="When the task was last updated")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result when completed")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if the task failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class A2AMessage(BaseModel):
    """Base message format for A2A communication."""
    message_id: UUID = Field(default_factory=uuid4, description="Unique message identifier")
    conversation_id: UUID = Field(default_factory=uuid4, description="Conversation identifier")
    message_type: MessageType = Field(..., description="Type of the message")
    sender_id: str = Field(..., description="ID of the sending agent")
    recipient_id: str = Field(..., description="ID of the intended recipient agent")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was sent")
    parts: List[MessagePart] = Field(default_factory=list, description="Message content parts")
    task: Optional[Task] = Field(None, description="Task details, if this is a task-related message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        return v or datetime.utcnow()

class A2AResponse(BaseModel):
    """Standard response format for A2A API calls."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if the operation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
