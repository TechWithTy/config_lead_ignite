"""
AIUsageAction and AIUsageLog models for tracking AI usage and actions across users.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

class AIActionType(str, Enum):
    generate_post = "generate_post"
    summarize = "summarize"
    analyze = "analyze"
    translate = "translate"
    image_generation = "image_generation"
    code_generation = "code_generation"
    workflow_trigger = "workflow_trigger"
    other = "other"

class AIUsageAction(BaseModel):
    user_id: str = Field(..., description="User performing the action")
    action_type: AIActionType = Field(..., description="Type of AI action performed")
    timestamp: str = Field(..., description="Time of action (ISO 8601)")
    input_tokens: Optional[int] = Field(None, description="Input tokens used")
    output_tokens: Optional[int] = Field(None, description="Output tokens generated")
    cost: Optional[float] = Field(None, description="Cost in credits or $ for this action")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional metadata (model, params, etc.)")

class AIUsageLog(BaseModel):
    """Tracks all AI usage actions for a user or globally."""
    user_id: Optional[str] = Field(None, description="User ID if per-user log, else global")
    actions: List[AIUsageAction] = Field(default_factory=list, description="List of AI actions performed")
    total_tokens: Optional[int] = Field(None, description="Total tokens used (input + output)")
    total_cost: Optional[float] = Field(None, description="Total cost in credits or $ for all actions")
    summary: Optional[Dict[str, float]] = Field(default_factory=dict, description="Aggregated usage stats")
