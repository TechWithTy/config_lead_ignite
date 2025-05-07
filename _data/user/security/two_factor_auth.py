from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .recovery_code import RecoveryCode

class TwoFactorMethod(str, Enum):
    sms = "sms"
    authenticator_app = "authenticator_app"
    email = "email"
    none = "none"

class TwoFactorAuth(BaseModel):
    """
    Represents a user's two-factor authentication settings, including explicit recovery codes for account recovery.
    """
    enabled: bool = Field(False, description="Is two-factor authentication enabled?")
    method: TwoFactorMethod = Field(TwoFactorMethod.none, description="2FA method (e.g., SMS, authenticator app, email)")
    last_verified_at: Optional[str] = Field(None, description="Last verification timestamp (ISO 8601)")
    recovery_codes: list["RecoveryCode"] = Field(default_factory=list, description="Explicit one-time use recovery codes for 2FA account recovery")
    device_info: Optional[str] = Field(None, description="Device info for 2FA, if applicable")
    # * Recovery codes are now tracked and auditable

