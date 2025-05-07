"""
GlobalTeam: Aggregates team members and invitations for unified team management.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from .team_member import TeamMember
from .invitation import Invitation

class GlobalTeam(BaseModel):
    team_members: List[TeamMember] = Field(default_factory=list, description="List of all team members")
    invitations: List[Invitation] = Field(default_factory=list, description="Pending or historical invitations")
    owner_id: Optional[str] = Field(None, description="User ID of the team/company owner")
    team_name: Optional[str] = Field(None, description="Name of the team or company")
    created_at: Optional[str] = Field(None, description="Timestamp when the team was created (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Timestamp when the team was last updated (ISO 8601)")
    # todo: Add fields for roles, permissions, audit logs, external integrations, etc.

    class Config:
        title = "GlobalTeam"
        arbitrary_types_allowed = True
