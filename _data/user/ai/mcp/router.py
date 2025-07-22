"""
FastAPI router for MCP (Model Context Protocol) endpoints.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .models import MCPRequest, MCPResponse, MCPTool
from .service import MCPService
from .exceptions import MCPError, ToolNotFoundError, InvalidRequestError

# Create router
router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get MCP service
def get_mcp_service() -> MCPService:
    """Get MCP service instance."""
    # In a real app, you would get the DB session from a dependency
    return MCPService()


class MCPRequestModel(BaseModel):
    """Request model for MCP operations."""
    operation: str
    parameters: Dict[str, Any] = {}
    context: Dict[str, Any] = {}


@router.post("/execute", response_model=MCPResponse)
async def execute_mcp_operation(
    request: Request,
    mcp_request: MCPRequestModel,
    mcp_service: MCPService = Depends(get_mcp_service)
) -> MCPResponse:
    """
    Execute an MCP operation.
    
    This endpoint processes MCP requests and returns the operation result.
    """
    try:
        # Extract headers for configuration overrides
        config_overrides = {}
        for key, value in request.headers.items():
            if key.lower().startswith('x-config-'):
                config_overrides[key] = value
        
        # Add config overrides to the context
        context = mcp_request.context or {}
        if config_overrides:
            context['config_overrides'] = config_overrides
        
        # Create the MCP request
        request = MCPRequest(
            operation=mcp_request.operation,
            parameters=mcp_request.parameters,
            context=context
        )
        
        # Process the request
        return await mcp_service.process_request(request)
        
    except MCPError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/tools", response_model=Dict[str, Dict[str, Any]])
async def list_available_tools(
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Dict[str, Any]]:
    """
    List all available MCP tools with their schemas.
    
    Returns a dictionary where keys are tool names and values are tool schemas.
    """
    return mcp_service.list_available_tools()


@router.get("/tools/{tool_name}", response_model=Dict[str, Any])
async def get_tool_schema(
    tool_name: str,
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """
    Get the schema for a specific tool.
    
    Args:
        tool_name: Name of the tool to get the schema for
        
    Returns:
        Dictionary containing the tool schema
    """
    tools = mcp_service.list_available_tools()
    if tool_name not in tools:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found"
        )
    return tools[tool_name]


def register_mcp_routes(app):
    """Register MCP routes with the FastAPI application."""
    app.include_router(router)
    return app
