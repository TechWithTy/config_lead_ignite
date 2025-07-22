"""
OpenRouter integration models for text generation.
"""
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime

from ..base_models import BaseAIConfig, StreamingConfig

class TextModelProvider(str, Enum):
    """Supported text model providers via OpenRouter."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    MISTRAL = "mistral"
    TOGETHER = "together"
    PERPLEXITY = "perplexity"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"
    CUSTOM = "custom"

class TextModelCapability(str, Enum):
    """Capabilities of text models."""
    TEXT = "text"
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    TOOLS = "tools"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"

class TextModelConfig(BaseModel):
    """Configuration for a specific text model."""
    model_id: str = Field(..., description="Model identifier")
    provider: TextModelProvider = Field(..., description="Model provider")
    name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Model description")
    context_length: int = Field(4096, description="Maximum context length in tokens")
    capabilities: List[TextModelCapability] = Field(
        default_factory=list,
        description="Supported capabilities"
    )
    is_default: bool = Field(False, description="Whether this is the default model")
    is_available: bool = Field(True, description="Whether the model is currently available")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class OpenRouterStreamConfig(StreamingConfig):
    """Configuration for OpenRouter streaming."""
    include_usage: bool = Field(True, description="Include token usage in stream")
    include_stop_reason: bool = Field(True, description="Include stop reason in final chunk")
    timeout: int = Field(60, description="Stream timeout in seconds")

class OpenRouterConfig(BaseAIConfig):
    """Configuration for OpenRouter API."""
    api_base: str = Field("https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    default_model: Optional[str] = Field(None, description="Default model ID to use")
    models: Dict[str, TextModelConfig] = Field(
        default_factory=dict,
        description="Configured text models"
    )
    streaming: OpenRouterStreamConfig = Field(
        default_factory=OpenRouterStreamConfig,
        description="Streaming configuration"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional HTTP headers to include in requests"
    )

    @field_validator('default_model')
    def validate_default_model(cls, v, values):
        if v and 'models' in values and v not in values['models']:
            raise ValueError(f"Default model {v} not found in configured models")
        return v

class TextGenerationRequest(BaseModel):
    """Request for text generation."""
    prompt: str = Field(..., description="Input prompt")
    model: Optional[str] = Field(None, description="Model ID to use")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    stream: bool = Field(False, description="Whether to stream the response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TextGenerationResponse(BaseModel):
    """Response from text generation."""
    text: str = Field(..., description="Generated text")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, int] = Field(
        default_factory=dict,
        description="Token usage information"
    )
    finish_reason: Optional[str] = Field(None, description="Reason for generation completion")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class TextStreamChunk(BaseModel):
    """A chunk of streaming text generation."""
    text: str = Field(..., description="Generated text chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage so far")
    finish_reason: Optional[str] = Field(None, description="Reason for completion if final")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
