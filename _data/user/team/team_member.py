from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class TeamMemberStatus(str, Enum):
    """Status of a team member's membership."""
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    REMOVED = "removed"

class TeamRole(str, Enum):
    """Available team roles with hierarchical permissions."""
    OWNER = "owner"       # Full access, can manage team settings and members
    ADMIN = "admin"       # Can manage members and most settings
    MEMBER = "member"     # Standard team member with basic access
    GUEST = "guest"       # Limited access (view-only in most cases)

class TeamMember(BaseModel):
    """Represents a member of a team with role-based access control.
    
    Attributes:
        id: Unique identifier for the team membership
        user_id: System-wide user ID
        team_id: ID of the team this membership belongs to
        role: Role within the team (owner/admin/member/guest)
        joined_at: When the user joined the team
        last_active: Last activity timestamp
        status: Current membership status
        metadata: Additional metadata (permissions, settings, etc.)
        created_at: When the membership was created
        updated_at: When the membership was last updated
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the team membership")
    user_id: UUID = Field(..., description="System-wide user ID")
    team_id: UUID = Field(..., description="ID of the team this membership belongs to")
    role: TeamRole = Field(TeamRole.MEMBER, description="Role within the team")
    joined_at: datetime = Field(default_factory=datetime.utcnow, description="When the user joined the team")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")
    status: TeamMemberStatus = Field(TeamMemberStatus.ACTIVE, description="Membership status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata and settings")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the membership was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the membership was last updated")

    # Validators
    @validator('role')
    def validate_role(cls, v, values):
        """Ensure only one owner exists per team."""
        if v == TeamRole.OWNER and 'team_id' in values:
            # In a real implementation, we'd check for existing owner here
            pass
        return v

    # Helper methods
    def has_permission(self, permission: str) -> bool:
        """Check if member has a specific permission based on their role."""
        # This would be expanded based on your permission system
        role_permissions = {
            TeamRole.OWNER: {'*'},
            TeamRole.ADMIN: {'manage_members', 'edit_team_settings'},
            TeamRole.MEMBER: {'view_team', 'create_content'},
            TeamRole.GUEST: {'view_team'}
        }
        return ('*' in role_permissions[self.role] or 
                permission in role_permissions.get(self.role, set()))

    def promote_to_admin(self) -> bool:
        """Promote member to admin role if not already an owner."""
        if self.role != TeamRole.OWNER:
            self.role = TeamRole.ADMIN
            self.updated_at = datetime.utcnow()
            return True
        return False

    def demote_to_member(self) -> bool:
        """Demote member to standard member role if not an owner."""
        if self.role == TeamRole.ADMIN:
            self.role = TeamRole.MEMBER
            self.updated_at = datetime.utcnow()
            return True
        return False

    def deactivate(self) -> None:
        """Deactivate the team membership."""
        self.status = TeamMemberStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def reactivate(self) -> None:
        """Reactivate a suspended membership."""
        if self.status == TeamMemberStatus.SUSPENDED:
            self.status = TeamMemberStatus.ACTIVE
            self.updated_at = datetime.utcnow()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
        use_enum_values = True
