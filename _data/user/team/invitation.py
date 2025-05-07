from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class InvitationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    revoked = "revoked"

class Invitation(BaseModel):
    email: str = Field(..., description="Email address of the invitee")
    sent_at: Optional[str] = Field(None, description="Timestamp when invitation was sent (ISO 8601)")
    accepted_at: Optional[str] = Field(None, description="Timestamp when invitation was accepted (ISO 8601)")
    expired_at: Optional[str] = Field(None, description="Timestamp when invitation expired (ISO 8601)")
    status: InvitationStatus = Field(InvitationStatus.pending, description="Current status of the invitation")
    invited_by: Optional[str] = Field(None, description="User ID or email of the inviter")
    oauth_provider: Optional[str] = Field(None, description="OAuth provider used for invitation, if any")
    # todo: Add token, message, or audit fields as needed
