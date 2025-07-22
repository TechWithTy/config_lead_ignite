from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class RoleName(str, Enum):
    """System roles with hierarchical permissions"""
    USER = "user"
    SUPPORT = "support"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class Role(BaseModel):
    """Role model for RBAC system"""
    id: UUID = Field(default_factory=uuid4)
    name: RoleName
    description: str
    permissions: List[str] = Field(default_factory=list)
    is_system: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission"""
        return permission in self.permissions

class UserRole(BaseModel):
    """Mapping between users and roles"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    role_id: UUID
    created_by: Optional[UUID] = None  # Who assigned this role
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }
    
    @validator('expires_at', pre=True, always=True)
    def validate_expires_at(cls, v, values):
        if v and v < datetime.utcnow():
            raise ValueError("Expiration date must be in the future")
        return v

# System roles with default permissions
SYSTEM_ROLES = {
    RoleName.USER: Role(
        name=RoleName.USER,
        description="Regular application user",
        permissions=[
            "self:read",
            "self:update",
            "content:create",
            "content:read:own"
        ],
        is_system=True
    ),
    RoleName.SUPPORT: Role(
        name=RoleName.SUPPORT,
        description="Support agent with limited admin access",
        permissions=[
            "user:read",
            "user:credit:adjust",
            "user:provisioning:retry",
            "audit_log:read",
            "event_log:read"
        ],
        is_system=True
    ),
    RoleName.ADMIN: Role(
        name=RoleName.ADMIN,
        description="System administrator",
        permissions=[
            "user:create",
            "user:read",
            "user:update",
            "user:delete",
            "user:impersonate",
            "user:role:assign",
            "audit_log:read",
            "event_log:read",
            "system:settings:update"
        ],
        is_system=True
    ),
    RoleName.SUPER_ADMIN: Role(
        name=RoleName.SUPER_ADMIN,
        description="Super administrator with all permissions",
        permissions=["*"],  # Wildcard for all permissions
        is_system=True
    )
}
