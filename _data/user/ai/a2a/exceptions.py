"""
Exceptions for the A2A (Agent-to-Agent) protocol implementation.
"""

class A2AError(Exception):
    """Base exception for all A2A-related errors."""
    pass

class AgentNotFoundError(A2AError):
    """Raised when a referenced agent cannot be found."""
    pass

class InvalidMessageError(A2AError):
    """Raised when a message is malformed or invalid."""
    pass

class TaskNotFoundError(A2AError):
    """Raised when a referenced task cannot be found."""
    pass

class CapabilityNotFoundError(A2AError):
    """Raised when a requested capability is not available."""
    pass

class AuthenticationError(A2AError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(A2AError):
    """Raised when an operation is not authorized."""
    pass

class RateLimitExceededError(A2AError):
    """Raised when rate limits are exceeded."""
    pass

class TimeoutError(A2AError):
    """Raised when an operation times out."""
    pass

class ValidationError(A2AError):
    """Raised when input validation fails."""
    pass

class CommunicationError(A2AError):
    """Raised when there is a communication error with another agent."""
    pass

class TaskExecutionError(A2AError):
    """Raised when a task fails to execute."""
    def __init__(self, task_id: str, message: str, original_error: Exception = None):
        self.task_id = task_id
        self.original_error = original_error
        super().__init__(f"Error executing task {task_id}: {message}")

class UnsupportedContentTypeError(A2AError):
    """Raised when an unsupported content type is encountered."""
    pass
