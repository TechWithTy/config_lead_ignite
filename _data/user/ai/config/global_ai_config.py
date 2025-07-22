from pydantic import BaseModel, Field
from config_lead_ignite._data.user.ai_config.llm import LLMConfig

class GlobalAIConfig(BaseModel):
    """
    Global AI context model, centralizing LLM configuration and other AI context state.
    """
    llm: LLMConfig = Field(default_factory=LLMConfig)
    # Add additional global AI context fields here as needed
