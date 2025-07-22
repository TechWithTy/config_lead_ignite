"""
Base models and interfaces for AI service integrations.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime

T = TypeVar('T')

class StreamEventType(str, Enum):
    """Types of events in a streaming response."""
    START = "start"
    CONTENT = "content"
    ERROR = "error"
    DONE = "done"

class StreamEvent(BaseModel, Generic[T]):
    """Represents an event in a streaming response."""
    event_type: StreamEventType = Field(..., description="Type of streaming event")
    data: Optional[T] = Field(None, description="Event data payload")
    error: Optional[str] = Field(None, description="Error message if event_type is ERROR")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class BaseAIConfig(BaseModel, ABC):
    """Base configuration for AI services."""
    enabled: bool = Field(True, description="Whether this service is enabled")
    api_key: Optional[str] = Field(None, description="API key for the service")
    model: str = Field(..., description="Default model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    timeout: int = Field(30, description="Request timeout in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator('api_key', always=True)
    def validate_api_key(cls, v, values):
        if not v and values.get('enabled', False):
            raise ValueError("API key is required when service is enabled")
        return v

class StreamingConfig(BaseModel):
    """Configuration for streaming responses."""
    enabled: bool = Field(True, description="Enable streaming")
    chunk_size: int = Field(1024, description="Size of each chunk in bytes")
    buffer_size: int = Field(8192, description="Size of the read buffer")
    format: str = Field("json", description="Stream format (json, text, binary)")

class BaseAIService(ABC):
    """Base class for AI service implementations."""
    
    @abstractmethod
    async def initialize(self):
        """Initialize the service with configuration."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response (blocking)."""
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> StreamEvent[str]:
        """Stream the response asynchronously."""
        yield

    @abstractmethod
    async def close(self):
        """Clean up resources."""
        pass
