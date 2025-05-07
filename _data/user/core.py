from pydantic import BaseModel, Field
from typing import Optional

class PII(BaseModel):
    """Personally Identifiable Information (PII) for the user.
    // todo: Ensure all PII fields are encrypted at rest in the DB layer.
    """
    user_id: str = Field(..., description="Internal unique user identifier")  # ! Must be unique (DB constraint)
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    profile_photo_url: Optional[str] = Field(None, description="URL to user's profile photo")
    date_of_birth: Optional[str] = Field(None, description="User's date of birth (ISO 8601)")
    gender: Optional[str] = Field(None, description="User's gender")

    def encrypt_fields(self):
        """
        // todo: Implement encryption for all PII fields before saving to DB.
        """
        pass

    def decrypt_fields(self):
        """
        // todo: Implement decryption for all PII fields after loading from DB.
        """
        pass

class ContactInfo(BaseModel):
    """User contact information."""
    email: str = Field(..., description="User's primary email address")
    alternate_email: Optional[str] = Field(None, description="User's alternate email address")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    address: Optional[str] = Field(None, description="Mailing address")

class LocationInfo(BaseModel):
    """User location details."""
    city: Optional[str] = Field(None, description="User's city")
    state: Optional[str] = Field(None, description="User's state/province")
    country: Optional[str] = Field(None, description="User's country")
    timezone: Optional[str] = Field(None, description="User's timezone")
    coordinates: Optional[str] = Field(None, description="Lat/long coordinates")

class SecuritySettings(BaseModel):
    """User security and authentication settings."""
    two_factor_enabled: bool = Field(False, description="Is 2FA enabled?")
    last_login: Optional[str] = Field(None, description="Last login timestamp (ISO 8601)")
    failed_login_attempts: int = Field(0, description="Failed login attempts")
    password_updated_at: Optional[str] = Field(None, description="Password last updated (ISO 8601)")

class NotificationSettings(BaseModel):
    """User notification preferences."""
    email_notifications: bool = Field(True, description="Receive email notifications?")
    sms_notifications: bool = Field(False, description="Receive SMS notifications?")
    push_notifications: bool = Field(False, description="Receive push notifications?")
    newsletter_opt_in: bool = Field(True, description="Subscribed to newsletters?")

class OnboardingStatus(BaseModel):
    """Tracks onboarding/completion steps."""
    completed: bool = Field(False, description="Onboarding complete?")
    steps_completed: int = Field(0, description="Number of steps completed")
    last_step: Optional[str] = Field(None, description="Last completed onboarding step")

class CoreIdentity(BaseModel):
    """Core user identity, referencing PII, contact, and location models."""
    pii: PII
    contact: ContactInfo
    location: LocationInfo
    security: SecuritySettings
    onboarding: OnboardingStatus
