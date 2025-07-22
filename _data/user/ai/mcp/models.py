"""
MCP (Model Context Protocol) data models for AI operations.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime


class MCPStatus(str, Enum):
    """Status of an MCP operation."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MCPResult(BaseModel):
    """Result of an MCP operation."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Result data")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MCPRequest(BaseModel):
    """Base request model for MCP operations."""
    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID")
    operation: str = Field(..., description="Name of the operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class MCPResponse(BaseModel):
    """Base response model for MCP operations."""
    request_id: UUID = Field(..., description="Corresponding request ID")
    status: MCPStatus = Field(..., description="Operation status")
    result: Optional[MCPResult] = Field(None, description="Operation result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    @validator('status')
    def set_completed_at(cls, v, values):
        if v in [MCPStatus.COMPLETED, MCPStatus.FAILED]:
            values['completed_at'] = datetime.utcnow()
        return v


class MCPTool(BaseModel):
    """Metadata for an MCP tool/operation."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    required: List[str] = Field(default_factory=list, description="Required parameters")
    handler: Optional[Callable] = Field(None, description="Handler function")


class MCPToolRegistry:
    """Registry for MCP tools."""
    _instance = None
    _tools: Dict[str, MCPTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPToolRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, tool: MCPTool) -> Callable:
        """Register a new tool."""
        def decorator(func: Callable) -> Callable:
            tool.handler = func
            cls._tools[tool.name] = tool
            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> Dict[str, MCPTool]:
        """List all registered tools."""
        return cls._tools.copy()
