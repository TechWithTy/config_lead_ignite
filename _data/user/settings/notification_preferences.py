from pydantic import BaseModel, Field
from typing import Optional

class NotificationPreferences(BaseModel):
    email_notifications: bool = Field(True, description="Receive notifications by email")
    sms_notifications: bool = Field(False, description="Receive notifications by SMS")
    push_notifications: bool = Field(False, description="Receive push notifications")
    marketing_opt_in: bool = Field(False, description="Receive marketing/promotional notifications")
    # todo: Add per-channel and per-event preferences
