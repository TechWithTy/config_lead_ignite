from pydantic import BaseModel, Field



class AICredits(BaseModel):
    id: str = Field(..., description="Unique AI credits record ID")
    allotted: int = Field(..., description="Allotted AI credits")
    used: int = Field(..., description="Used AI credits")
    reset_in_days: int = Field(..., description="Days until credits reset")
    subscription_id: str = Field(..., description="UserProfileSubscription ID")

class LeadCredits(BaseModel):
    id: str = Field(..., description="Unique lead credits record ID")
    allotted: int = Field(..., description="Allotted lead credits")
    used: int = Field(..., description="Used lead credits")
    reset_in_days: int = Field(..., description="Days until credits reset")
    subscription_id: str = Field(..., description="UserProfileSubscription ID")

class SkipTraceCredits(BaseModel):
    id: str = Field(..., description="Unique skip trace credits record ID")
    allotted: int = Field(..., description="Allotted skip trace credits")
    used: int = Field(..., description="Used skip trace credits")
    reset_in_days: int = Field(..., description="Days until credits reset")
    subscription_id: str = Field(..., description="UserProfileSubscription ID")
