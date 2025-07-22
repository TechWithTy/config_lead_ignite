"""
Thread and participant models for AI chat.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import Field, field_validator
from uuid import UUID, uuid4

from .base import BaseModelWithTimestamps, ParticipantRole

class Participant(BaseModelWithTimestamps):
    """Represents a participant in a chat thread."""
    thread_id: UUID = Field(..., description="ID of the thread")
    user_id: UUID = Field(..., description="ID of the user/AI")
    role: ParticipantRole = Field(ParticipantRole.USER, description="Role in the thread")
    display_name: Optional[str] = Field(None, description="Display name in this thread")
    avatar_url: Optional[str] = Field(None, description="Avatar URL for this thread")
    is_active: bool = Field(True, description="Whether the participant is active")
    last_read_at: Optional[datetime] = Field(None, description="When the participant last read messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator('display_name')
    def set_display_name(cls, v):
        """Set a default display name if none provided."""
        return v or f"User {str(uuid4())[:8]}"

class ThreadSettings(BaseModelWithTimestamps):
    """Configuration settings for a chat thread."""
    allow_reactions: bool = Field(True, description="Allow message reactions")
    allow_threads: bool = Field(True, description="Allow threaded replies")
    allow_edits: bool = Field(True, description="Allow message editing")
    allow_deletes: bool = Field(True, description="Allow message deletion")
    require_approval: bool = Field(False, description="Require approval for new participants")
    slow_mode: bool = Field(False, description="Enable slow mode")
    slow_mode_delay: int = Field(5, ge=0, description="Slow mode delay in seconds")
    max_message_length: int = Field(5000, gt=0, description="Maximum message length in characters")
    max_attachments: int = Field(10, ge=0, description="Maximum attachments per message")
    max_attachment_size: int = Field(25 * 1024 * 1024, description="Maximum file size in bytes")
    allowed_file_types: List[str] = Field(
        default_factory=lambda: ["image/*", "audio/*", "video/*", "application/pdf"],
        description="Allowed MIME types for file uploads"
    )

class Thread(BaseModelWithTimestamps):
    """Represents a chat thread or conversation."""
    title: Optional[str] = Field(None, description="Thread title")
    description: Optional[str] = Field(None, description="Thread description")
    is_group: bool = Field(False, description="Whether this is a group thread")
    is_public: bool = Field(False, description="Whether the thread is publicly visible")
    is_archived: bool = Field(False, description="Whether the thread is archived")
    settings: ThreadSettings = Field(default_factory=ThreadSettings, description="Thread settings")
    participants: List[Participant] = Field(default_factory=list, description="Thread participants")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def add_participant(self, user_id: UUID, role: ParticipantRole = ParticipantRole.USER, **kwargs) -> Participant:
        """Add a participant to the thread."""
        # Check if user is already a participant
        if any(p.user_id == user_id for p in self.participants):
            raise ValueError(f"User {user_id} is already a participant in this thread")
        
        participant = Participant(
            thread_id=self.id,
            user_id=user_id,
            role=role,
            **kwargs
        )
        self.participants.append(participant)
        self.updated_at = datetime.utcnow()
        return participant

    def remove_participant(self, user_id: UUID) -> bool:
        """Remove a participant from the thread."""
        initial_count = len(self.participants)
        self.participants = [p for p in self.participants if p.user_id != user_id]
        if len(self.participants) < initial_count:
            self.updated_at = datetime.utcnow()
            return True
        return False

    def update_participant_role(self, user_id: UUID, role: ParticipantRole) -> bool:
        """Update a participant's role in the thread."""
        for participant in self.participants:
            if participant.user_id == user_id:
                participant.role = role
                participant.updated_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                return True
        return False

    def get_participant(self, user_id: UUID) -> Optional[Participant]:
        """Get a participant by user ID."""
        for participant in self.participants:
            if participant.user_id == user_id:
                return participant
        return None
