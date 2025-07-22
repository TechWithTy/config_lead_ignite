"""
GlobalKanban: Manages kanban boards, their states, and tasks with AI capabilities.
"""
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from uuid import UUID, uuid4

from .kanban_state import KanbanState, ColumnType
from .kanban_task import KanbanTask, TaskType, TaskStatus, TaskPriority, AIActionType


class BoardSettings(BaseModel):
    """Configuration settings for a kanban board."""
    id: UUID = Field(default_factory=uuid4, description="Unique settings ID")
    board_id: UUID = Field(..., description="Board these settings belong to")
    
    # Board behavior
    allow_ai_suggestions: bool = Field(True, description="Whether to show AI-suggested tasks")
    auto_archive_completed: bool = Field(True, description="Auto-archive completed tasks")
    archive_after_days: int = Field(30, ge=1, description="Days before archiving completed tasks")
    
    # Permissions
    allow_public_comments: bool = Field(False, description="Allow comments from non-members")
    allow_task_creation: bool = Field(True, description="Allow creating new tasks")
    allow_task_reassignment: bool = Field(True, description="Allow reassigning tasks")
    
    # UI/UX
    default_view: str = Field("board", description="Default view (board, list, calendar)")
    card_cover_images: bool = Field(True, description="Show cover images on task cards")
    
    # Integration settings
    external_sync_enabled: bool = Field(False, description="Enable sync with external systems")
    external_sync_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for external system integration"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class BoardMember(BaseModel):
    """Represents a member of a kanban board with their role."""
    user_id: UUID = Field(..., description="ID of the user")
    board_id: UUID = Field(..., description="ID of the board")
    role: str = Field("member", description="Role in the board (admin, editor, viewer)")
    joined_at: datetime = Field(default_factory=datetime.utcnow, description="When the user joined")
    
    # Permissions (can be overridden per user)
    can_edit: bool = Field(True, description="Can edit board content")
    can_invite: bool = Field(False, description="Can invite new members")
    can_configure: bool = Field(False, description="Can change board settings")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class KanbanBoard(BaseModel):
    """Represents a kanban board with states, tasks, and members."""
    id: UUID = Field(default_factory=uuid4, description="Unique board ID")
    name: str = Field(..., max_length=100, description="Board name")
    description: Optional[str] = Field(None, description="Board description")
    organization_id: UUID = Field(..., description="Organization this board belongs to")
    
    # Relationships (not stored, resolved at runtime)
    states: List[KanbanState] = Field(
        default_factory=list,
        description="All states/columns in this board"
    )
    tasks: List[KanbanTask] = Field(
        default_factory=list,
        description="All tasks in this board"
    )
    members: List[BoardMember] = Field(
        default_factory=list,
        description="Users with access to this board"
    )
    
    # Board settings
    settings: BoardSettings = Field(
        default_factory=lambda: BoardSettings(board_id=uuid4()),
        description="Board configuration"
    )
    
    # Metadata
    is_public: bool = Field(False, description="Whether the board is publicly visible")
    is_template: bool = Field(False, description="Whether this is a template board")
    created_by: UUID = Field(..., description="User ID who created the board")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
    
    def update_timestamps(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def get_state_by_id(self, state_id: UUID) -> Optional[KanbanState]:
        """Get a state by its ID."""
        return next((s for s in self.states if s.id == state_id), None)
    
    def get_tasks_in_state(self, state_id: UUID) -> List[KanbanTask]:
        """Get all tasks in a specific state."""
        return [t for t in self.tasks if t.state_id == state_id]
    
    def get_ai_suggested_tasks(self) -> List[KanbanTask]:
        """Get all AI-suggested tasks."""
        return [t for t in self.tasks if t.is_ai_generated]
    
    def get_tasks_for_user(self, user_id: UUID) -> List[KanbanTask]:
        """Get all tasks assigned to a specific user."""
        return [t for t in self.tasks if t.assignee_id == user_id]


class GlobalKanban(BaseModel):
    """Global kanban manager that handles multiple boards and cross-board operations."""
    # Core data
    boards: Dict[UUID, KanbanBoard] = Field(
        default_factory=dict,
        description="All kanban boards, keyed by board ID"
    )
    
    # Caches (not persisted)
    _user_boards_cache: Dict[UUID, Set[UUID]] = Field(
        default_factory=dict,
        description="Cache of user ID to set of board IDs they can access"
    )
    
    class Config:
        title = "GlobalKanban"
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    
    # Board management
    def add_board(self, board: KanbanBoard) -> None:
        """Add a new board to the global kanban."""
        if board.id in self.boards:
            raise ValueError(f"Board with ID {board.id} already exists")
        self.boards[board.id] = board
        self._update_user_boards_cache(board)
    
    def get_board(self, board_id: UUID) -> Optional[KanbanBoard]:
        """Get a board by ID."""
        return self.boards.get(board_id)
    
    def get_user_boards(self, user_id: UUID) -> List[KanbanBoard]:
        """Get all boards accessible by a user."""
        if user_id not in self._user_boards_cache:
            self._rebuild_user_boards_cache(user_id)
        return [self.boards[bid] for bid in self._user_boards_cache.get(user_id, set())]
    
    def _update_user_boards_cache(self, board: KanbanBoard) -> None:
        """Update the user boards cache for all members of a board."""
        for member in board.members:
            if member.user_id not in self._user_boards_cache:
                self._user_boards_cache[member.user_id] = set()
            self._user_boards_cache[member.user_id].add(board.id)
    
    def _rebuild_user_boards_cache(self, user_id: UUID) -> None:
        """Rebuild the user boards cache for a specific user."""
        self._user_boards_cache[user_id] = {
            bid for bid, board in self.boards.items()
            if any(m.user_id == user_id for m in board.members)
        }
