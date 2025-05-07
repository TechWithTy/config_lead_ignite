"""
UserSecurity: Unified security model for user authentication, permissions, platform access, and two-factor authentication.
- Combines: auth_models, permissions_models, platform_access, two_factor_auth
- Use this as the single import for user security domain logic.
"""
from pydantic import BaseModel, Field
from typing import  Optional

from .auth_models import ConnectedAccounts
from .permissions_models import UserPermissions
from .platform_access import PlatformAccess
from .two_factor_auth import TwoFactorAuth

class UserSecurity(BaseModel):
    connected_accounts: Optional[ConnectedAccounts] = Field(None, description="User's connected OAuth/social accounts")
    permissions: Optional[UserPermissions] = Field(None, description="User's permissions within the platform/team")
    platform_access: Optional[PlatformAccess] = Field(None, description="User's platform access and role info")
    two_factor_auth: Optional[TwoFactorAuth] = Field(None, description="User's two-factor authentication settings")

    class Config:
        title = "UserSecurity"
        arbitrary_types_allowed = True


# Global UserSettings model (using TwoFactorAuth and Auth-related models)
class UserSettings(BaseModel):
    two_factor_auth: Optional[TwoFactorAuth] = Field(None, description="Two-factor authentication settings")
    connected_accounts: Optional[ConnectedAccounts] = Field(None, description="OAuth/social accounts")
    # Add more global user settings fields as needed (e.g., notification preferences, theme, etc.)

    class Config:
        title = "UserSettings"
        arbitrary_types_allowed = True
