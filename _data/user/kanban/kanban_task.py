from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum
from typing import Optional

class KanbanTaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    blocked = "blocked"

class KanbanTask(BaseModel):
    """Represents a single task/card in a Kanban board."""
    id: str = Field(..., description="Unique Kanban task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    state_id: str = Field(..., description="KanbanState ID for this task")
    assigned_to: Optional[str] = Field(None, description="User ID assigned to this task")
    due_date: Optional[str] = Field(None, description="Due date (ISO 8601)")
    created_at: Optional[str] = Field(None, description="Task creation timestamp (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Task last update timestamp (ISO 8601)")
    status: KanbanTaskStatus = Field(KanbanTaskStatus.todo, description="Task status")
    priority: Optional[int] = Field(None, description="Priority of the task (lower = higher priority)")
    comments: Optional[list] = Field(default_factory=list, description="Comments or discussion on the task")
    # todo: Add subtasks, attachments, and audit fields
