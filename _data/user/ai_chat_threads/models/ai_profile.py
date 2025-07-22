"""
AI profile and behavior configuration for chat threads.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import Field, field_validator, HttpUrl
from uuid import UUID, uuid4
from .base import BaseModelWithTimestamps

from .ai_config.text_models import TextModelProvider
from .ai_config.hey_gen.models import HeyGenAvatarConfig
from .ai_config.vapi.models import VoiceConfig

class AIBehaviorPreset(str, Enum):
    """Predefined behavior presets for AI participants."""
    ASSISTANT = "assistant"
    CHATBOT = "chatbot"
    TUTOR = "tutor"
    SUPPORT = "support"
    SALES = "sales"
    CUSTOM = "custom"

class AIRole(str, Enum):
    """Roles that an AI can take in a conversation."""
    ASSISTANT = "assistant"
    EXPERT = "expert"
    MODERATOR = "moderator"
    TRANSLATOR = "translator"
    SUMMARIZER = "summarizer"
    CUSTOM = "custom"

class AIConfig(BaseModelWithTimestamps):
    """Configuration for an AI participant in a chat thread."""
    name: str = Field(..., description="Display name of the AI")
    description: str = Field("", description="Description of the AI's purpose")
    behavior_preset: AIBehaviorPreset = Field(
        AIBehaviorPreset.ASSISTANT,
        description="Predefined behavior preset"
    )
    role: AIRole = Field(AIRole.ASSISTANT, description="Role in the conversation")
    
    # Text generation configuration
    text_model_provider: TextModelProvider = Field(
        TextModelProvider.OPENAI,
        description="Default text model provider"
    )
    text_model: str = Field("gpt-4", description="Default text model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2048, gt=0, description="Maximum tokens to generate")
    
    # Voice configuration
    voice_enabled: bool = Field(False, description="Enable voice capabilities")
    voice_config: Optional[VoiceConfig] = Field(None, description="Voice configuration")
    
    # Avatar configuration
    avatar_enabled: bool = Field(False, description="Enable avatar capabilities")
    avatar_config: Optional[HeyGenAvatarConfig] = Field(None, description="Avatar configuration")
    
    # Behavior configuration
    system_prompt: str = Field(
        "You are a helpful AI assistant.",
        description="System prompt that defines the AI's behavior"
    )
    allowed_actions: List[str] = Field(
        default_factory=lambda: ["text", "image", "search"],
        description="List of allowed actions for this AI"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional configuration and metadata"
    )

    @field_validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("AI name cannot be empty")
        return v.strip()
    
    def update_behavior(self, **updates) -> None:
        """Update the AI's behavior configuration."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

class AIProfile(BaseModelWithTimestamps):
    """Represents an AI profile that can be used across threads."""
    user_id: UUID = Field(..., description="ID of the user who owns this profile")
    name: str = Field(..., description="Profile name")
    description: str = Field("", description="Profile description")
    is_public: bool = Field(False, description="Whether this profile is public")
    config: AIConfig = Field(default_factory=AIConfig, description="AI configuration")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    def update_config(self, **updates) -> None:
        """Update the AI configuration."""
        self.config.update_behavior(**updates)
        self.updated_at = datetime.utcnow()

class AIThreadParticipant(BaseModelWithTimestamps):
    """Represents an AI participant in a specific thread."""
    thread_id: UUID = Field(..., description="ID of the thread")
    ai_profile_id: UUID = Field(..., description="ID of the AI profile")
    config_overrides: Dict[str, Any] = Field(
        default_factory=dict,
        description="Thread-specific configuration overrides"
    )
    is_active: bool = Field(True, description="Whether the AI is active in the thread")
    last_active_at: Optional[datetime] = Field(None, description="When the AI was last active")
    
    def get_effective_config(self, base_config: AIConfig) -> AIConfig:
        """Get the effective configuration with thread-specific overrides applied."""
        if not self.config_overrides:
            return base_config
        
        # Create a copy of the base config
        config_dict = base_config.model_dump()
        
        # Apply overrides
        for key, value in self.config_overrides.items():
            if key in config_dict:
                if isinstance(config_dict[key], dict) and isinstance(value, dict):
                    config_dict[key].update(value)
                else:
                    config_dict[key] = value
        
        return AIConfig(**config_dict)
