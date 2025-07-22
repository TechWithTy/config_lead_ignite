"""
Decorators for MCP (Model Context Protocol) tools.
"""
from typing import Any, Callable, Dict, Optional, TypeVar, cast
from functools import wraps
from .models import MCPTool, MCPToolRegistry

F = TypeVar('F', bound=Callable[..., Any])

def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    required: Optional[list] = None
) -> Callable[[F], F]:
    """
    Decorator to register a function as an MCP tool.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        parameters: JSON Schema for tool parameters
        required: List of required parameter names
    """
    def decorator(func: F) -> F:
        nonlocal name, description, parameters, required
        
        # Use function name if name not provided
        if name is None:
            name = func.__name__
            
        # Use docstring as description if not provided
        if description is None and func.__doc__:
            description = func.__doc__.strip()
            
        # Create and register the tool
        tool = MCPTool(
            name=name,
            description=description or "",
            parameters=parameters or {},
            required=required or []
        )
        
        # Register the tool with the registry
        MCPToolRegistry.register(tool)(func)
        
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)
            
        return cast(F, wrapper)
    return decorator



def validate_parameters(func: F) -> F:
    """
    Decorator to validate function parameters against the tool's schema.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the tool from the registry
        tool = MCPToolRegistry.get_tool(func.__name__)
        if not tool:
            raise ValueError(f"Tool '{func.__name__}' not found in registry")
            
        # Validate required parameters
        for param in tool.required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
                
        # TODO: Add more comprehensive parameter validation
        # based on the tool.parameters schema
        
        return await func(*args, **kwargs)
    
    return cast(F, wrapper)