from pydantic import BaseModel, Field

class UserPermissions(BaseModel):
    """Represents a user's permissions within a team or organization."""
    id: str = Field(..., description="Unique user permissions record ID")
    can_generate_leads: bool = Field(..., description="Can generate leads?")
    can_start_campaigns: bool = Field(..., description="Can start campaigns?")
    can_view_reports: bool = Field(..., description="Can view reports?")
    can_manage_team: bool = Field(..., description="Can manage team?")
    can_manage_subscription: bool = Field(..., description="Can manage subscription?")
    can_access_ai: bool = Field(..., description="Can access AI features?")
    can_move_company_tasks: bool = Field(..., description="Can move company tasks?")
    can_edit_company_profile: bool = Field(..., description="Can edit company profile?")
    team_member_id: str = Field(..., description="Associated TeamMember ID")
