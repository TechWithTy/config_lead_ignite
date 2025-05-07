from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum
from typing import Optional

class TeamMemberStatus(str, Enum):
    active = "active"
    invited = "invited"
    removed = "removed"

class TeamMember(BaseModel):
    """Represents a member of a team or company."""
    user_id: str = Field(..., description="User ID of the team member")
    role: str = Field(..., description="Role of the team member in the team/company")
    joined_at: Optional[str] = Field(None, description="Timestamp when the user joined the team (ISO 8601)")
    is_owner: bool = Field(False, description="Is this user the team/company owner?")
    status: TeamMemberStatus = Field(TeamMemberStatus.active, description="Membership status (active, invited, removed)")
    # todo: Add permissions, audit, and external identity fields
