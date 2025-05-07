from pydantic import BaseModel, Field
from typing import Optional

from typing import Optional

class KanbanState(BaseModel):
    """Represents a single state/column in a Kanban board."""
    id: str = Field(..., description="Unique Kanban state ID")
    name: str = Field(..., description="Name of the Kanban state (e.g., To Do, In Progress, Done)")
    order: int = Field(..., description="Order of the state in the Kanban board")
    color: Optional[str] = Field(None, description="Color for the state")
    board_id: Optional[str] = Field(None, description="Board ID this state belongs to")
    created_at: Optional[str] = Field(None, description="Created timestamp (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Updated timestamp (ISO 8601)")
    # todo: Add user ownership and automation fields
