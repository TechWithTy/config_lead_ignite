from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum
from typing import Optional, Dict

class IntegrationStatus(str, Enum):
    connected = "connected"
    disconnected = "disconnected"
    error = "error"

class Integration(BaseModel):
    """Represents a third-party integration connection for a user or company."""
    name: str = Field(..., description="Name of the integration (e.g., Slack, Zapier)")
    provider: Optional[str] = Field(None, description="Integration provider or platform")
    connected_at: Optional[str] = Field(None, description="Timestamp when integration was connected (ISO 8601)")
    status: IntegrationStatus = Field(IntegrationStatus.connected, description="Current status of the integration")
    config: Optional[Dict[str, str]] = Field(default_factory=dict, description="Integration-specific configuration")
    last_error: Optional[str] = Field(None, description="Last error message if integration failed")
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO 8601)")
    # todo: Add tokens, webhook URLs, and audit fields as needed
