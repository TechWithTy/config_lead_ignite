"""
Vapi.ai integration models for voice interfaces.
"""
from enum import Enum
from typing import Dict, Optional,Any
from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime

from ..base_models import BaseAIConfig, StreamingConfig

class VoiceGender(str, Enum):
    """Gender of the voice."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"
    UNSPECIFIED = "unspecified"

class VoiceProvider(str, Enum):
    """Supported voice providers."""
    ELEVEN_LABS = "eleven_labs"
    GOOGLE = "google"
    AMAZON = "amazon"
    MICROSOFT = "microsoft"
    IBM = "ibm"
    CUSTOM = "custom"

class VoiceEmotion(str, Enum):
    """Supported voice emotions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUST = "disgust"
    SURPRISED = "surprised"

class VoiceConfig(BaseModel):
    """Configuration for a voice."""
    voice_id: str = Field(..., description="Unique identifier for the voice")
    name: str = Field(..., description="Display name")
    provider: VoiceProvider = Field(..., description="Voice provider")
    gender: VoiceGender = Field(VoiceGender.NEUTRAL, description="Voice gender")
    language: str = Field("en-US", description="Voice language code")
    is_default: bool = Field(False, description="Whether this is the default voice")
    sample_rate: int = Field(24000, description="Sample rate in Hz")
    is_streaming: bool = Field(True, description="Whether the voice supports streaming")
    emotion: VoiceEmotion = Field(VoiceEmotion.NEUTRAL, description="Default emotion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class VapiStreamConfig(StreamingConfig):
    """Configuration for Vapi streaming."""
    sample_rate: int = Field(24000, description="Audio sample rate in Hz")
    channels: int = Field(1, description="Number of audio channels")
    format: str = Field("pcm_s16le", description="Audio format")
    latency: int = Field(2, description="Target latency in segments")
    buffer_size: int = Field(8192, description="Buffer size in bytes")
    auto_reconnect: bool = Field(True, description="Automatically reconnect on disconnection")

class VapiConfig(BaseAIConfig):
    """Configuration for Vapi API."""
    api_base: str = Field("https://api.vapi.ai/v1", description="Vapi API base URL")
    default_voice_id: Optional[str] = Field(None, description="Default voice ID to use")
    streaming: VapiStreamConfig = Field(
        default_factory=VapiStreamConfig,
        description="Streaming configuration"
    )
    voices: Dict[str, VoiceConfig] = Field(
        default_factory=dict,
        description="Configured voices"
    )
    silence_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Silence threshold for voice activity detection"
    )
    noise_reduction: bool = Field(True, description="Enable noise reduction")
    echo_cancellation: bool = Field(True, description="Enable echo cancellation")
    auto_gain_control: bool = Field(True, description="Enable auto gain control")

    @field_validator('default_voice_id')
    def validate_default_voice(cls, v, values):
        if v and 'voices' in values and v not in values['voices']:
            raise ValueError(f"Default voice {v} not found in configured voices")
        return v

class VoiceRequest(BaseModel):
    """Request for voice synthesis or recognition."""
    text: Optional[str] = Field(None, description="Text to synthesize")
    voice_id: Optional[str] = Field(None, description="Voice ID to use")
    emotion: Optional[VoiceEmotion] = Field(None, description="Emotion to use")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Playback speed")
    pitch: float = Field(0.0, ge=-20.0, le=20.0, description="Pitch adjustment in semitones")
    stream: bool = Field(False, description="Whether to stream the response")
    language: Optional[str] = Field(None, description="Language code (if different from voice default)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class VoiceResponse(BaseModel):
    """Response from voice synthesis or recognition."""
    audio_url: Optional[HttpUrl] = Field(None, description="URL to the generated audio")
    audio_data: Optional[bytes] = Field(None, description="Raw audio data")
    duration_ms: Optional[int] = Field(None, description="Duration of the audio in milliseconds")
    text: Optional[str] = Field(None, description="Transcribed text (for recognition)")
    voice_id: Optional[str] = Field(None, description="Voice ID used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            bytes: lambda v: "<binary data>" if v else None
        }

class VoiceStreamChunk(BaseModel):
    """A chunk of streaming audio data."""
    audio_data: bytes = Field(..., description="Raw audio data chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    text: Optional[str] = Field(None, description="Transcribed text if available")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
