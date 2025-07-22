"""
Data models for GoHighLevel (GHL) integration.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from uuid import UUID, uuid4


class GHLAccountStatus(str, Enum):
    """Status of a GHL account connection."""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"
    PENDING = "pending_authorization"


class GHLAccountTier(str, Enum):
    """Available GHL account tiers."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    AGENCY = "agency"
    ENTERPRISE = "enterprise"


class GHLWebhookEventType(str, Enum):
    """Supported GHL webhook event types."""
    CONTACT_CREATED = "contact.added"
    CONTACT_UPDATED = "contact.updated"
    CONTACT_DELETED = "contact.deleted"
    CALENDAR_EVENT_CREATED = "calendar.event.created"
    CALENDAR_EVENT_UPDATED = "calendar.event.updated"
    CALENDAR_EVENT_DELETED = "calendar.event.deleted"
    OPPORTUNITY_CREATED = "opportunity.created"
    OPPORTUNITY_UPDATED = "opportunity.updated"
    TASK_COMPLETED = "task.completed"


class GHLAccount(BaseModel):
    """Represents a connected GHL account."""
    id: UUID = Field(default_factory=uuid4, description="Internal account ID")
    user_id: UUID = Field(..., description="ID of the user who owns this account")
    ghl_account_id: str = Field(..., description="GHL's account ID")
    location_id: str = Field(..., description="GHL location ID")
    name: str = Field(..., description="Account name in GHL")
    tier: GHLAccountTier = Field(..., description="GHL account tier")
    status: GHLAccountStatus = Field(
        default=GHLAccountStatus.DISCONNECTED,
        description="Connection status"
    )
    access_token: Optional[str] = Field(
        None, 
        description="OAuth access token (encrypted in DB)",
        exclude=True
    )
    refresh_token: Optional[str] = Field(
        None, 
        description="OAuth refresh token (encrypted in DB)",
        exclude=True
    )
    expires_at: Optional[datetime] = Field(
        None, 
        description="When the access token expires"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional account metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the account was connected"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the account was last updated"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class GHLSubaccount(BaseModel):
    """Represents a subaccount in GHL (location)."""
    id: UUID = Field(default_factory=uuid4, description="Internal subaccount ID")
    ghl_account_id: str = Field(..., description="Parent GHL account ID")
    location_id: str = Field(..., description="GHL location ID")
    name: str = Field(..., description="Subaccount/location name")
    timezone: str = Field("UTC", description="Account timezone")
    is_active: bool = Field(True, description="Whether this subaccount is active")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional subaccount metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the subaccount was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the subaccount was last updated"
    )

    @validator('timezone')
    def validate_timezone(cls, v):
        try:
            import pytz
            pytz.timezone(v)
            return v
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {v}")


class GHLWebhookEvent(BaseModel):
    """Represents a webhook event received from GHL."""
    id: UUID = Field(default_factory=uuid4, description="Internal event ID")
    event_type: GHLWebhookEventType = Field(..., description="Type of webhook event")
    ghl_account_id: str = Field(..., description="Related GHL account ID")
    location_id: str = Field(..., description="Related GHL location ID")
    resource_id: str = Field(..., description="ID of the affected resource")
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw webhook payload"
    )
    processed: bool = Field(
        False,
        description="Whether this event has been processed"
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="When this event was processed"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the event was received"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
