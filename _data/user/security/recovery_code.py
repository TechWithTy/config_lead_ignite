from pydantic import BaseModel, Field
from typing import Optional

class RecoveryCode(BaseModel):
    code: str = Field(..., description="One-time recovery code for 2FA recovery")
    used: bool = Field(False, description="Has this code been used?")
    generated_at: Optional[str] = Field(None, description="When was this code generated? (ISO 8601)")
    used_at: Optional[str] = Field(None, description="When was this code used? (ISO 8601)")

    class Config:
        title = "RecoveryCode"
        arbitrary_types_allowed = True
