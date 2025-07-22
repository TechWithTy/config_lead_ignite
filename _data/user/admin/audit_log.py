from enum import Enum
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class AuditResourceType(str, Enum):
    """Types of resources that can be audited"""
    USER = "user"
    ROLE = "role"
    CREDIT = "credit"
    PROVISIONING = "provisioning"
    SYSTEM = "system"

class AuditAction(str, Enum):
    """Possible audit actions"""
    # User actions
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_IMPERSONATED = "user_impersonated"
    
    # Role actions
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    
    # Credit actions
    CREDITS_ADJUSTED = "credits_adjusted"
    
    # Provisioning actions
    PROVISIONING_RETRIED = "provisioning_retried"
    
    # System actions
    SETTINGS_UPDATED = "settings_updated"
    
    # Auth actions
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"

class AuditLog(BaseModel):
    """Audit log entry for tracking admin and system actions"""
    id: UUID = Field(default_factory=uuid4)
    action: AuditAction
    resource_type: AuditResourceType
    resource_id: Optional[Union[UUID, str]] = None
    
    # Who performed the action
    actor_id: UUID
    actor_type: str = "user"  # Could be 'user', 'system', 'api_key', etc.
    
    # Action details
    details: Dict[str, Any] = Field(default_factory=dict)
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

    @classmethod
    def create(
        cls,
        action: AuditAction,
        resource_type: AuditResourceType,
        actor_id: UUID,
        resource_id: Optional[Union[UUID, str]] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditLog':
        """Helper to create a new audit log entry"""
        return cls(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

# Helper functions for common audit log scenarios
def log_user_impersonation(
    admin_id: UUID,
    target_user_id: UUID,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Create an audit log entry for user impersonation"""
    return AuditLog.create(
        action=AuditAction.USER_IMPERSONATED,
        resource_type=AuditResourceType.USER,
        resource_id=target_user_id,
        actor_id=admin_id,
        details={"impersonated_user_id": str(target_user_id)},
        ip_address=ip_address,
        user_agent=user_agent
    )

def log_credit_adjustment(
    admin_id: UUID,
    user_id: UUID,
    credit_type: str,
    amount: float,
    reason: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Create an audit log entry for credit adjustments"""
    return AuditLog.create(
        action=AuditAction.CREDITS_ADJUSTED,
        resource_type=AuditResourceType.CREDIT,
        resource_id=user_id,
        actor_id=admin_id,
        details={
            "credit_type": credit_type,
            "amount": amount,
            "reason": reason
        },
        ip_address=ip_address,
        user_agent=user_agent
    )

def log_provisioning_retry(
    admin_id: UUID,
    user_id: UUID,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Create an audit log entry for provisioning retry"""
    return AuditLog.create(
        action=AuditAction.PROVISIONING_RETRIED,
        resource_type=AuditResourceType.PROVISIONING,
        resource_id=user_id,
        actor_id=admin_id,
        details={"retry_initiated_by": str(admin_id)},
        ip_address=ip_address,
        user_agent=user_agent
    )
