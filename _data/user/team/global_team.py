"""
GlobalTeam: Centralized team management with members, invitations, activity tracking, and credit management.
"""
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from enum import Enum
import logging

from .team_member import TeamMember, TeamRole, TeamMemberStatus
from .invitation import Invitation, InvitationStatus

logger = logging.getLogger(__name__)

class TeamActivityType(str, Enum):
    """Types of team activities that can be tracked."""
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    MEMBER_ROLE_CHANGED = "member_role_changed"
    INVITATION_SENT = "invitation_sent"
    INVITATION_ACCEPTED = "invitation_accepted"
    TEAM_UPDATED = "team_updated"
    CREDITS_ADDED = "credits_added"
    CREDITS_USED = "credits_used"

class TeamActivity(BaseModel):
    """Represents an activity event within a team."""
    id: UUID = Field(default_factory=uuid4, description="Unique activity ID")
    type: TeamActivityType = Field(..., description="Type of activity")
    user_id: UUID = Field(..., description="ID of the user who performed the action")
    target_user_id: Optional[UUID] = Field(None, description="ID of the affected user, if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context about the activity")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the activity occurred")

class TeamCreditPool(BaseModel):
    """Tracks available and used credits for a team."""
    total_credits: float = Field(0.0, description="Total credits available to the team")
    used_credits: float = Field(0.0, description="Credits that have been used")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When credits were last updated")
    
    @property
    def available_credits(self) -> float:
        """Calculate remaining available credits."""
        return max(0.0, self.total_credits - self.used_credits)
    
    def add_credits(self, amount: float) -> bool:
        """Add credits to the pool."""
        if amount <= 0:
            logger.warning(f"Attempted to add non-positive credits: {amount}")
            return False
        self.total_credits += amount
        self.last_updated = datetime.utcnow()
        return True
    
    def use_credits(self, amount: float) -> bool:
        """Use credits if available."""
        if amount <= 0:
            logger.warning(f"Attempted to use non-positive credits: {amount}")
            return False
        if self.available_credits < amount:
            logger.warning(f"Insufficient credits: {self.available_credits} < {amount}")
            return False
        self.used_credits += amount
        self.last_updated = datetime.utcnow()
        return True

class GlobalTeam(BaseModel):
    """
    Represents a team or organization with members, invitations, and shared resources.
    
    Attributes:
        id: Unique team identifier
        name: Display name of the team
        slug: URL-friendly team identifier
        owner_id: User ID of the team owner
        members: List of team members
        invitations: Pending team invitations
        credit_pool: Shared credit pool for the team
        settings: Team-specific settings
        metadata: Additional team data
        created_at: When the team was created
        updated_at: When the team was last updated
    """
    id: UUID = Field(default_factory=uuid4, description="Unique team identifier")
    name: str = Field(..., description="Display name of the team", min_length=2, max_length=100)
    slug: str = Field(..., description="URL-friendly team identifier", regex=r'^[a-z0-9-]+$')
    owner_id: UUID = Field(..., description="User ID of the team owner")
    members: List[TeamMember] = Field(default_factory=list, description="List of team members")
    invitations: List[Invitation] = Field(default_factory=list, description="Pending invitations")
    credit_pool: TeamCreditPool = Field(default_factory=TeamCreditPool, description="Team's credit pool")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Team settings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional team data")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the team was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the team was last updated")
    
    # Validators
    @validator('slug')
    def slug_must_be_lowercase(cls, v):
        return v.lower()
    
    # Team Member Management
    def add_member(self, user_id: UUID, role: TeamRole = TeamRole.MEMBER) -> Optional[TeamMember]:
        """Add a new member to the team."""
        if any(m.user_id == user_id for m in self.members):
            logger.warning(f"User {user_id} is already a member of team {self.id}")
            return None
            
        member = TeamMember(
            user_id=user_id,
            team_id=self.id,
            role=role,
            status=TeamMemberStatus.ACTIVE
        )
        self.members.append(member)
        self.updated_at = datetime.utcnow()
        return member
    
    def remove_member(self, user_id: UUID) -> bool:
        """Remove a member from the team."""
        initial_count = len(self.members)
        self.members = [m for m in self.members if m.user_id != user_id]
        if len(self.members) < initial_count:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_member(self, user_id: UUID) -> Optional[TeamMember]:
        """Get a team member by user ID."""
        for member in self.members:
            if member.user_id == user_id:
                return member
        return None
    
    def update_member_role(self, user_id: UUID, new_role: TeamRole) -> bool:
        """Update a member's role."""
        for member in self.members:
            if member.user_id == user_id and member.role != new_role:
                member.role = new_role
                member.updated_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    # Invitation Management
    def create_invitation(self, email: str, role: str, invited_by: UUID) -> Optional[Invitation]:
        """Create a new team invitation."""
        # Check for existing pending invitation
        if any(i.email.lower() == email.lower() and i.status == InvitationStatus.PENDING 
               for i in self.invitations):
            logger.warning(f"Pending invitation already exists for {email}")
            return None
            
        invitation = Invitation(
            email=email,
            team_id=self.id,
            role=role,
            invited_by=invited_by
        )
        self.invitations.append(invitation)
        self.updated_at = datetime.utcnow()
        return invitation
    
    def accept_invitation(self, token: str, user_id: UUID) -> bool:
        """Accept a pending invitation."""
        for invitation in self.invitations:
            if invitation.token == token and invitation.status == InvitationStatus.PENDING:
                if invitation.accept():
                    self.add_member(user_id, invitation.role)
                    self.updated_at = datetime.utcnow()
                    return True
        return False
    
    # Activity Tracking
    def log_activity(self, activity_type: TeamActivityType, user_id: UUID, 
                    target_user_id: UUID = None, **metadata) -> TeamActivity:
        """Log a new team activity."""
        activity = TeamActivity(
            type=activity_type,
            user_id=user_id,
            target_user_id=target_user_id,
            metadata=metadata
        )
        # In a real implementation, this would be stored in a database
        # For now, we'll just log it
        logger.info(f"Team Activity - {activity_type}: {activity.json()}")
        return activity
    
    # Credit Management
    def add_credits(self, amount: float, added_by: UUID) -> bool:
        """Add credits to the team's pool."""
        if self.credit_pool.add_credits(amount):
            self.log_activity(
                TeamActivityType.CREDITS_ADDED,
                user_id=added_by,
                amount=amount,
                new_balance=self.credit_pool.available_credits
            )
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def use_credits(self, amount: float, used_by: UUID) -> bool:
        """Use credits from the team's pool."""
        if self.credit_pool.use_credits(amount):
            self.log_activity(
                TeamActivityType.CREDITS_USED,
                user_id=used_by,
                amount=amount,
                remaining_balance=self.credit_pool.available_credits
            )
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    # Helper methods
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization."""
        result = self.dict(exclude={"members", "invitations"})
        result["members"] = [m.dict() for m in self.members]
        result["invitations"] = [i.dict() for i in self.invitations]
        result["available_credits"] = self.credit_pool.available_credits
        result["member_count"] = len(self.members)
        result["pending_invitations"] = sum(
            1 for i in self.invitations 
            if i.status == InvitationStatus.PENDING
        )
        return result
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
        use_enum_values = True
        arbitrary_types_allowed = True
