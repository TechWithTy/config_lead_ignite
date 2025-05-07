from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ConnectedAccounts(BaseModel):
    id: str = Field(..., description="Unique connected accounts ID")
    user_id: Optional[str] = Field(None, description="User ID this account belongs to")
    oauth_data: List["OAuthData"] = Field(default_factory=list, description="Associated OAuth data entries")

class OAuthProvider(str, Enum):
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"
    LINKEDIN = "LINKEDIN"
    TWITTER = "TWITTER"

class OAuthData(BaseModel):
    id: str = Field(..., description="Unique OAuth data entry ID")
    provider: OAuthProvider = Field(..., description="OAuth provider")
    username: Optional[str] = Field(None, description="Social username")
    page_id: Optional[str] = Field(None, description="Page ID for social provider")
    company_id: Optional[str] = Field(None, description="Company ID for social provider")
    handle: Optional[str] = Field(None, description="Handle")
    access_token: str = Field(..., description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    expires_in: int = Field(..., description="Expiration time in seconds")
    token_type: str = Field(..., description="Token type")
    scope: Optional[str] = Field(None, description="Scopes granted")
    last_refreshed_at: Optional[str] = Field(None, description="Last refresh timestamp (ISO 8601)")
    connected_account_id: str = Field(..., description="ConnectedAccounts ID")

# allow forward references
ConnectedAccounts.update_forward_refs()
