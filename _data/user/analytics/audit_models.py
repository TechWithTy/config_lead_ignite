from pydantic import BaseModel, Field
from typing import Optional, List

class AuditLog(BaseModel):
    id: str = Field(..., description="Unique audit log ID")
    user_id: str = Field(..., description="User ID associated with the action")
    action: str = Field(..., description="Action performed")
    timestamp: str = Field(..., description="Timestamp of the action (ISO 8601)")
    ip_address: Optional[str] = Field(None, description="IP address of the actor")
    metadata: Optional[dict] = Field(None, description="Additional metadata")

class TaskActivity(BaseModel):
    id: str = Field(..., description="Unique task activity record ID")
    action: str = Field(..., description="Action performed on task")
    timestamp: str = Field(..., description="Timestamp of the activity (ISO 8601)")
    performed_by: str = Field(..., description="Actor who performed the activity")
    task_tracking_id: str = Field(..., description="Associated TaskTracking ID")

class TaskTracking(BaseModel):
    id: str = Field(..., description="Unique task tracking record ID")
    total_tasks: int = Field(..., description="Total tasks count")
    tasks_assigned: int = Field(..., description="Number of tasks assigned")
    tasks_completed: int = Field(..., description="Number of tasks completed")
    tasks_in_progress: int = Field(..., description="Number of tasks in progress")
    assigned_tasks: List[dict] = Field(default_factory=list, description="List of assigned tasks summaries")
    task_history: List[TaskActivity] = Field(default_factory=list, description="History of task activities")

class ActivityLog(BaseModel):
    id: str = Field(..., description="Unique activity log ID")
    user_id: str = Field(..., description="User ID associated with the activity")
    action: str = Field(..., description="Action performed")
    timestamp: str = Field(..., description="Timestamp of the activity (ISO 8601)")
    performed_by: str = Field(..., description="Actor who performed the activity")
    task_tracking_id: str = Field(..., description="Associated TaskTracking ID")
    team_member_id: Optional[str] = Field(None, description="Associated TeamMember ID if applicable")
    user_agent: Optional[str] = Field(None, description="User agent string of the actor")
