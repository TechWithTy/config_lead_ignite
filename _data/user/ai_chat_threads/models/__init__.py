"""
AI Chat Threads - Core Models

This package contains the core data models for the AI chat threads system.
"""
from .base import (
    BaseModelWithTimestamps,
    MessageType,
    MessageStatus,
    ParticipantRole
)

from .message import (
    Attachment,
    MessageContent,
    Message,
    MessageUpdate
)

from .thread import (
    Thread,
    ThreadSettings,
    Participant
)

from .ai_profile import (
    AIBehaviorPreset,
    AIRole,
    AIConfig,
    AIProfile,
    AIThreadParticipant
)

# Re-export all models for easier imports
__all__ = [
    # Base models
    'BaseModelWithTimestamps',
    'MessageType',
    'MessageStatus',
    'ParticipantRole',
    
    # Message models
    'Attachment',
    'MessageContent',
    'Message',
    'MessageUpdate',
    
    # Thread models
    'Thread',
    'ThreadSettings',
    'Participant',
    
    # AI Profile models
    'AIBehaviorPreset',
    'AIRole',
    'AIConfig',
    'AIProfile',
    'AIThreadParticipant',
]
