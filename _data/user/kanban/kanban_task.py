from enum import Enum
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime, date
from uuid import UUID, uuid4


class TaskStatus(str, Enum):
    """Status of a task in the workflow."""
    PENDING_APPROVAL = "pending_approval"
    PENDING_USER_ACTION = "pending_user_action"
    PENDING_AI_EXECUTION = "pending_ai_execution"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    """Priority levels for tasks."""
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0


class TaskType(str, Enum):
    """Type of task, used for categorization and routing."""
    MANUAL = "manual"
    AI_SUGGESTED = "ai_suggested"
    AI_AUTOMATED = "ai_automated"
    FOLLOW_UP = "follow_up"
    ENRICHMENT = "enrichment"
    NOTIFICATION = "notification"


class AIActionType(str, Enum):
    """Types of actions the AI can perform on tasks."""
    SEND_FOLLOW_UP_SMS = "send_follow_up_sms"
    SEND_FOLLOW_UP_EMAIL = "send_follow_up_email"
    ENRICH_LEAD = "enrich_lead"
    SCHEDULE_MEETING = "schedule_meeting"
    CREATE_TASK = "create_task"
    UPDATE_CRM = "update_crm"


class TaskMetadata(BaseModel):
    """Additional metadata for tasks, especially AI-related ones."""
    ai_confidence: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="Confidence score of the AI's suggestion (0-1)"
    )
    ai_reasoning: Optional[str] = Field(
        None, 
        description="Explanation of why the AI suggested this task"
    )
    source: Optional[str] = Field(
        None,
        description="Source that triggered this task (e.g., 'lead_activity', 'user_created')"
    )
    external_references: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="External references (e.g., CRM IDs, email IDs, etc.)"
    )
    custom_fields: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom fields specific to the task type"
    )


class KanbanTask(BaseModel):
    """Represents a single task/card in a Kanban board with AI capabilities."""
    # Core task fields
    id: UUID = Field(default_factory=uuid4, description="Unique Kanban task ID")
    title: str = Field(..., max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    
    # Relationships
    state_id: UUID = Field(..., description="KanbanState ID for this task")
    board_id: UUID = Field(..., description="Board ID this task belongs to")
    organization_id: UUID = Field(..., description="Organization ID that owns this task")
    assignee_id: Optional[UUID] = Field(None, description="User ID assigned to this task")
    reporter_id: UUID = Field(..., description="User ID who created/reported this task")
    lead_id: Optional[UUID] = Field(None, description="Lead/Deal ID this task is associated with")
    parent_task_id: Optional[UUID] = Field(None, description="Parent task ID if this is a subtask")
    
    # Task type and status
    type: TaskType = Field(TaskType.MANUAL, description="Type of task")
    status: TaskStatus = Field(TaskStatus.PENDING_USER_ACTION, description="Current status of the task")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Priority level")
    
    # AI-specific fields
    is_ai_generated: bool = Field(False, description="Whether this task was generated by AI")
    ai_action_type: Optional[AIActionType] = Field(
        None,
        description="Type of AI action to be performed (if applicable)"
    )
    ai_metadata: TaskMetadata = Field(
        default_factory=TaskMetadata,
        description="AI-specific metadata and context"
    )
    
    # Dates and timing
    due_date: Optional[date] = Field(None, description="Due date for the task")
    start_date: Optional[date] = Field(None, description="Planned start date")
    completed_at: Optional[datetime] = Field(None, description="When the task was completed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Task details
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization and filtering"
    )
    attachments: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of file attachments with name and URL"
    )
    
    # Relationships to other systems
    external_id: Optional[str] = Field(
        None,
        description="External ID from another system (e.g., CRM, email, etc.)"
    )
    external_url: Optional[HttpUrl] = Field(
        None,
        description="URL to view this task in an external system"
    )
    
    # Constraints and validation
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: str
        }
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()
    
    def update_timestamps(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self, by_user_id: UUID):
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_by = by_user_id
        self.update_timestamps()
    
    def is_ai_actionable(self) -> bool:
        """Check if this task can be actioned by AI."""
        return (
            self.ai_action_type is not None 
            and self.status == TaskStatus.PENDING_AI_EXECUTION
            and not self.completed_at
        )
