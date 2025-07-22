"""
Exceptions for the GHL integration.
"""
from typing import Optional, Dict, Any


class GHLBaseException(Exception):
    """Base exception for all GHL-related errors."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class GHLAPIError(GHLBaseException):
    """Raised when there's an error communicating with the GHL API."""
    def __init__(self, message: str, status_code: int = 500, response: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"GHL API Error: {message}",
            status_code=status_code,
            details={"response": response}
        )


class GHLConnectionError(GHLBaseException):
    """Raised when there's an error connecting to GHL services."""
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(
            f"GHL Connection Error: {message}",
            status_code=status_code
        )


class GHLAuthorizationError(GHLBaseException):
    """Raised when there's an authorization error with GHL."""
    def __init__(self, message: str = "Invalid or expired GHL credentials"):
        super().__init__(
            f"GHL Authorization Error: {message}",
            status_code=401
        )


class GHLValidationError(GHLBaseException):
    """Raised when there's a validation error with GHL data."""
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(
            f"GHL Validation Error: {message}",
            status_code=422,
            details={"field_errors": field_errors or {}}
        )


class GHLWebhookError(GHLBaseException):
    """Raised when there's an error processing a GHL webhook."""
    def __init__(self, message: str, status_code: int = 400, event_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"GHL Webhook Error: {message}",
            status_code=status_code,
            details={"event_data": event_data}
        )
