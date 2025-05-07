"""
GlobalKanban: Aggregates kanban board states and tasks for unified kanban management.
"""
from pydantic import BaseModel, Field
from typing import List
from .kanban_state import KanbanState
from .kanban_task import KanbanTask

class GlobalKanban(BaseModel):
    states: List[KanbanState] = Field(default_factory=list, description="All kanban board states for the user")
    tasks: List[KanbanTask] = Field(default_factory=list, description="All kanban tasks for the user")
    # todo: Add fields for board metadata, swimlanes, audit logs, etc.

    class Config:
        title = "GlobalKanban"
        arbitrary_types_allowed = True
