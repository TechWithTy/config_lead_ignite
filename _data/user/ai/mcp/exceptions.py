"""
Exceptions for the MCP (Model Context Protocol) system.
"""

class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    pass


class ToolNotFoundError(MCPError):
    """Raised when a requested tool is not found in the registry."""
    pass


class InvalidRequestError(MCPError):
    """Raised when an invalid MCP request is received."""
    pass


class ToolExecutionError(MCPError):
    """Raised when a tool fails to execute."""
    def __init__(self, tool_name: str, message: str, original_error: Exception = None):
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(f"Error executing tool '{tool_name}': {message}")


class ValidationError(MCPError):
    """Raised when input validation fails."""
    pass


class AuthenticationError(MCPError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(MCPError):
    """Raised when a user is not authorized to perform an action."""
    pass


class RateLimitExceededError(MCPError):
    """Raised when rate limits are exceeded."""
    pass
