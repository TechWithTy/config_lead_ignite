from pydantic import BaseModel, Field, validator, HttpUrl, EmailStr
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import secrets
import string

class InvitationStatus(str, Enum):
    """Status of a team invitation."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

class InvitationRole(str, Enum):
    """Role being offered in the invitation."""
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

class Invitation(BaseModel):
    """Represents an invitation to join a team with a specific role.
    
    Attributes:
        id: Unique invitation identifier
        token: Secure random token for invitation URL
        email: Email of the invitee
        team_id: ID of the team being invited to
        role: Role being offered
        status: Current status of the invitation
        expires_at: When the invitation expires
        accepted_at: When the invitation was accepted
        created_at: When the invitation was created
        updated_at: When the invitation was last updated
        invited_by: ID of the user who sent the invitation
        metadata: Additional invitation data
    """
    id: UUID = Field(default_factory=uuid4, description="Unique invitation identifier")
    token: str = Field(default_factory=lambda: ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)),
                      description="Secure random token for invitation URL")
    email: EmailStr = Field(..., description="Email address of the invitee")
    team_id: UUID = Field(..., description="ID of the team being invited to")
    role: InvitationRole = Field(InvitationRole.MEMBER, description="Role being offered")
    status: InvitationStatus = Field(InvitationStatus.PENDING, description="Current status")
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=7),
        description="When the invitation expires"
    )
    accepted_at: Optional[datetime] = Field(None, description="When invitation was accepted")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When invitation was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When invitation was last updated")
    invited_by: UUID = Field(..., description="ID of the user who sent the invitation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional invitation data")
    
    # Validators
    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()
    
    @validator('expires_at')
    def expires_at_must_be_future(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("Expiration must be in the future")
        return v
    
    # Helper methods
    def is_expired(self) -> bool:
        """Check if the invitation has expired."""
        return datetime.utcnow() > self.expires_at
    
    def accept(self) -> bool:
        """Mark the invitation as accepted."""
        if self.status == InvitationStatus.PENDING and not self.is_expired():
            self.status = InvitationStatus.ACCEPTED
            self.accepted_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def revoke(self) -> bool:
        """Revoke the invitation."""
        if self.status == InvitationStatus.PENDING:
            self.status = InvitationStatus.REVOKED
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_invitation_url(self, base_url: str) -> str:
        """Generate the full invitation URL."""
        return f"{base_url}/join-team?token={self.token}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime serialization."""
        result = self.dict()
        result['expires_at'] = self.expires_at.isoformat()
        if self.accepted_at:
            result['accepted_at'] = self.accepted_at.isoformat()
        return result
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
        use_enum_values = True
