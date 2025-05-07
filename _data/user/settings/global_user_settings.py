"""
UserSettings: Global user settings model for the app.
Includes authentication data, OAuth provider info, and other user-level preferences.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

from config_lead_ignite._data.user.settings.notification_preferences import NotificationPreferences
from config_lead_ignite._data.user.settings.integrations.integration import Integration
from config_lead_ignite._data.user.security.global_user_security import UserSecurity


class ThemePreference(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

# --- Global UserSettings model ---
class GlobalUserSettings(BaseModel):
    notification_preferences: Optional[NotificationPreferences] = Field(None, description="User notification preferences")
    user_security: Optional[UserSecurity] = Field(None, description="Aggregated user security settings (auth, permissions, 2FA, etc.)")
    theme_preference: ThemePreference = Field(ThemePreference.SYSTEM, description="UI theme preference (light/dark/system)")
    integrations: Optional[list[Integration]] = Field(default_factory=list, description="List of user integrations (e.g., Slack, Zapier, etc.)")
    # Add additional global user settings fields as needed

    class Config:
        title = "UserSettings"
        arbitrary_types_allowed = True
