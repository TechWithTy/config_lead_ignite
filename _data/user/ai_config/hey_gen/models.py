"""
HeyGen integration models for avatar streaming and video generation.
"""
from typing import Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime

from ..base_models import BaseAIConfig, StreamingConfig

class AvatarStyle(str, Enum):
    """Available avatar styles in HeyGen."""
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    ANIME = "anime"
    CUSTOM = "custom"

class Emotion(str, Enum):
    """Supported emotions for avatars."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"

class AvatarPosition(str, Enum):
    """Position of the avatar in the frame."""
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"

class HeyGenAvatarConfig(BaseModel):
    """Configuration for a HeyGen avatar."""
    avatar_id: str = Field(..., description="Unique identifier for the avatar")
    style: AvatarStyle = Field(AvatarStyle.REALISTIC, description="Visual style of the avatar")
    default_emotion: Emotion = Field(Emotion.NEUTRAL, description="Default emotion")
    position: AvatarPosition = Field(AvatarPosition.CENTER, description="Position in the frame")
    background_url: Optional[HttpUrl] = Field(None, description="Custom background URL")
    voice_id: Optional[str] = Field(None, description="Default voice ID for speech")
    lip_sync: bool = Field(True, description="Enable lip-syncing to audio")
    resolution: str = Field("1080p", description="Output resolution (e.g., 720p, 1080p, 4K)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class HeyGenStreamConfig(StreamingConfig):
    """Configuration for HeyGen streaming."""
    low_latency: bool = Field(True, description="Optimize for low latency")
    buffer_size: int = Field(4096, description="Buffer size for streaming data")
    auto_reconnect: bool = Field(True, description="Automatically reconnect on disconnection")
    max_retries: int = Field(3, description="Maximum number of reconnection attempts")

class HeyGenConfig(BaseAIConfig):
    """Configuration for HeyGen API."""
    api_base: str = Field("https://api.heygen.com/v1", description="HeyGen API base URL")
    default_avatar_id: Optional[str] = Field(None, description="Default avatar ID to use")
    default_voice_id: Optional[str] = Field(None, description="Default voice ID to use")
    streaming: HeyGenStreamConfig = Field(
        default_factory=HeyGenStreamConfig,
        description="Streaming configuration"
    )
    avatars: Dict[str, HeyGenAvatarConfig] = Field(
        default_factory=dict,
        description="Configured avatars"
    )

    @field_validator('default_avatar_id')
    def validate_default_avatar(cls, v, values):
        if v and 'avatars' in values and v not in values['avatars']:
            raise ValueError(f"Default avatar {v} not found in configured avatars")
        return v

class HeyGenStreamState(BaseModel):
    """State for an active HeyGen streaming session."""
    session_id: str = Field(..., description="Unique session ID")
    avatar_id: str = Field(..., description="Active avatar ID")
    voice_id: str = Field(..., description="Active voice ID")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    last_active: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    is_active: bool = Field(True, description="Whether the session is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class HeyGenResponse(BaseModel):
    """Standard response from HeyGen API."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    request_id: Optional[str] = Field(None, description="Unique request ID for support")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
