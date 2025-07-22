from enum import Enum
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class EventType(str, Enum):
    """Types of events that can be logged"""
    # User events
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_PROFILE_UPDATE = "user_profile_update"
    
    # Campaign events
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_PAUSED = "campaign_paused"
    CAMPAIGN_COMPLETED = "campaign_completed"
    CAMPAIGN_FAILED = "campaign_failed"
    
    # Content events
    CONTENT_GENERATED = "content_generated"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_EDITED = "content_edited"
    
    # Billing events
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPDATED = "subscription_updated"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    
    # System events
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    
    # Integration events
    INTEGRATION_CONNECTED = "integration_connected"
    INTEGRATION_DISCONNECTED = "integration_disconnected"
    INTEGRATION_ERROR = "integration_error"
    
    # Support events
    SUPPORT_TICKET_CREATED = "support_ticket_created"
    SUPPORT_TICKET_UPDATED = "support_ticket_updated"
    SUPPORT_TICKET_CLOSED = "support_ticket_closed"

class EventLog(BaseModel):
    """Model for logging user and system events"""
    id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    
    # Who performed the action (if any)
    user_id: Optional[UUID] = None
    
    # What resource this event is about (if any)
    resource_type: Optional[str] = None
    resource_id: Optional[Union[UUID, str]] = None
    
    # Event details
    details: Dict[str, Any] = Field(default_factory=dict)
    
    # Context information
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }
    
    @validator('details', pre=True)
    def validate_details(cls, v):
        """Ensure details is JSON serializable"""
        if not isinstance(v, dict):
            raise ValueError("Details must be a dictionary")
        return v

# Helper functions for common event logging scenarios
def log_user_event(
    event_type: EventType,
    user_id: UUID,
    resource_type: Optional[str] = None,
    resource_id: Optional[Union[UUID, str]] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> EventLog:
    """Log a user-initiated event"""
    return EventLog(
        event_type=event_type,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent
    )

def log_system_event(
    event_type: EventType,
    details: Optional[Dict[str, Any]] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[Union[UUID, str]] = None
) -> EventLog:
    """Log a system-generated event"""
    return EventLog(
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {}
    )

def log_integration_event(
    event_type: EventType,
    integration_name: str,
    details: Dict[str, Any],
    user_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[Union[UUID, str]] = None
) -> EventLog:
    """Log an integration-related event"""
    event_details = {
        "integration": integration_name,
        **details
    }
    return EventLog(
        event_type=event_type,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=event_details
    )

class EventFilter(BaseModel):
    """Filter criteria for querying events"""
    event_types: Optional[List[EventType]] = None
    user_id: Optional[UUID] = None
    resource_type: Optional[str] = None
    resource_id: Optional[Union[UUID, str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def to_query_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters"""
        params: Dict[str, Any] = {}
            
        if self.event_types:
            params['event_type__in'] = ",".join(self.event_types)
        if self.user_id:
            params['user_id'] = str(self.user_id)
        if self.resource_type:
            params['resource_type'] = self.resource_type
        if self.resource_id:
            params['resource_id'] = str(self.resource_id)
        if self.start_date:
            params['created_at__gte'] = self.start_date.isoformat()
        if self.end_date:
            params['created_at__lte'] = self.end_date.isoformat()
            
        return params
