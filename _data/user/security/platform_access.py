from pydantic import BaseModel, Field
from typing import List
from config._data.user.utils import RoleType, Permission

class PlatformAccess(BaseModel):
    """Platform role, permissions, and status."""
    role: RoleType = Field(RoleType.user, description="User role in SaaS platform")
    permissions: List[Permission] = Field(
        default_factory=lambda: [Permission.view_dashboard, Permission.edit_profile],
        description="List of permissions granted to user",
    )
    is_active: bool = Field(True, description="Is the user account active?")
    is_verified: bool = Field(False, description="Has the user verified their email?")
    is_company_owner: bool = Field(False, description="Is the user the owner/admin of the company?")
