from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4


class ColumnType(str, Enum):
    """Type of the kanban column, used for special handling in the UI/automation."""
    DEFAULT = "default"
    AI_SUGGESTED = "ai_suggested"
    INTAKE = "intake"
    ARCHIVE = "archive"


class KanbanState(BaseModel):
    """Represents a single state/column in a Kanban board."""
    id: UUID = Field(default_factory=uuid4, description="Unique Kanban state ID")
    name: str = Field(..., max_length=100, description="Name of the Kanban state (e.g., To Do, In Progress, Done)")
    description: Optional[str] = Field(None, max_length=500, description="Description of the column's purpose")
    order: int = Field(0, ge=0, description="Order of the state in the Kanban board")
    color: str = Field("#e0e0e0", description="Color for the state")
    type: ColumnType = Field(ColumnType.DEFAULT, description="Type of the column for special handling")
    
    # Relationships
    board_id: UUID = Field(..., description="Board ID this state belongs to")
    organization_id: UUID = Field(..., description="Organization ID that owns this board")
    
    # Metadata
    is_default: bool = Field(False, description="Whether this is a default system column")
    is_active: bool = Field(True, description="Whether this column is active")
    created_by: UUID = Field(..., description="User ID who created this column")
    updated_by: Optional[UUID] = Field(None, description="User ID who last updated this column")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last updated timestamp")
    
    # Automation settings
    auto_archive_days: Optional[int] = Field(
        None, 
        ge=1, 
        description="Automatically archive tasks after X days in this column"
    )
    auto_assign_team_id: Optional[UUID] = Field(
        None,
        description="Automatically assign tasks to this team when moved to this column"
    )
    
    # Constraints and validation
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Column name cannot be empty")
        return v.strip()
    
    def update_timestamps(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
