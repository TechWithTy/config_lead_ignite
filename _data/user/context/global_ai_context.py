"""
GlobalAIContext: Aggregates all AI-related configuration and context for a user or organization.
"""
from pydantic import BaseModel, Field
from typing import Optional
from .ai_config import AIConfig

class GlobalAIContext(BaseModel):
    ai_config: AIConfig = Field(default_factory=AIConfig, description="General AI configuration and instructions")
    # todo: Add fields for AI usage logs, LLM statistics, API keys, user preferences, etc.
    # Optionally add advanced context for multi-LLM, prompt history, or audit logs.

    class Config:
        title = "GlobalAIContext"
        arbitrary_types_allowed = True
