"""
A2A (Agent-to-Agent) Protocol Implementation

This package provides an implementation of the A2A protocol for building
interoperable AI agents. The A2A protocol enables agents to discover each other's
capabilities, exchange messages, and collaborate on tasks.
"""
from .models import (
    A2AMessage,
    A2AResponse,
    MessageType,
    TaskStatus,
    ContentType,
    MessagePart,
    Task,
    AgentCard,
    AgentCapability
)

from .service import A2AService
from .example_router import router, register_a2a_routes

from .exceptions import (
    A2AError,
    AgentNotFoundError,
    AuthenticationError,
    AuthorizationError,
    CapabilityNotFoundError,
    CommunicationError,
    InvalidMessageError,
    RateLimitExceededError,
    TaskExecutionError,
    TaskNotFoundError,
    TimeoutError,
    UnsupportedContentTypeError,
    ValidationError
)

__all__ = [
    # Core Models
    'A2AMessage',
    'A2AResponse',
    'MessageType',
    'TaskStatus',
    'ContentType',
    'MessagePart',
    'Task',
    'AgentCard',
    'AgentCapability',
    
    # Service
    'A2AService',
    
    # Router
    'router',
    'register_a2a_routes',
    
    # Exceptions
    'A2AError',
    'AgentNotFoundError',
    'AuthenticationError',
    'AuthorizationError',
    'CapabilityNotFoundError',
    'CommunicationError',
    'InvalidMessageError',
    'RateLimitExceededError',
    'TaskExecutionError',
    'TaskNotFoundError',
    'TimeoutError',
    'UnsupportedContentTypeError',
    'ValidationError'
]
