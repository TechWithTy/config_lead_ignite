"""
MCP (Model Context Protocol) service for handling AI operations.
"""
import json
import logging
from typing import Any, Dict, Optional, List, Type, TypeVar, Union
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, ValidationError

from .models import (
    MCPRequest,
    MCPResponse,
    MCPResult,
    MCPStatus,
    MCPTool,
    MCPToolRegistry
)
from .exceptions import MCPError, ToolNotFoundError, InvalidRequestError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class MCPService:
    """Service for handling MCP operations."""
    
    def __init__(self, db_session=None):
        """Initialize the MCP service.
        
        Args:
            db_session: Database session for persistent storage
        """
        self.db_session = db_session
        self.tool_registry = MCPToolRegistry()
        
    async def process_request(
        self,
        request_data: Union[Dict[str, Any], MCPRequest]
    ) -> MCPResponse:
        """Process an MCP request.
        
        Args:
            request_data: Request data as dict or MCPRequest instance
            
        Returns:
            MCPResponse: Response containing the operation result
        """
        try:
            # Parse and validate the request
            if not isinstance(request_data, MCPRequest):
                request = MCPRequest(**request_data)
            else:
                request = request_data
                
            logger.info(f"Processing MCP request: {request.request_id}")
            
            # Get the tool for this operation
            tool = self.tool_registry.get_tool(request.operation)
            if not tool or not tool.handler:
                raise ToolNotFoundError(f"Unknown operation: {request.operation}")
            
            # Execute the tool
            try:
                result = await tool.handler(**request.parameters, context=request.context)
                
                # Convert result to MCPResult if it's not already
                if not isinstance(result, MCPResult):
                    result = MCPResult(
                        success=True,
                        data=result if isinstance(result, dict) else {"result": result}
                    )
                
                return MCPResponse(
                    request_id=request.request_id,
                    status=MCPStatus.COMPLETED,
                    result=result
                )
                
            except Exception as e:
                logger.error(f"Error executing tool {request.operation}: {str(e)}", exc_info=True)
                return MCPResponse(
                    request_id=request.request_id,
                    status=MCPStatus.FAILED,
                    result=MCPResult(
                        success=False,
                        error=str(e),
                        metadata={"error_type": e.__class__.__name__}
                    )
                )
                
        except ValidationError as e:
            logger.error(f"Invalid MCP request: {str(e)}")
            return MCPResponse(
                request_id=getattr(request, 'request_id', uuid4()),
                status=MCPStatus.FAILED,
                result=MCPResult(
                    success=False,
                    error=f"Invalid request: {str(e)}",
                    metadata={"error_type": "ValidationError"}
                )
            )
            
        except Exception as e:
            logger.error(f"Unexpected error processing MCP request: {str(e)}", exc_info=True)
            return MCPResponse(
                request_id=getattr(request, 'request_id', uuid4()),
                status=MCPStatus.FAILED,
                result=MCPResult(
                    success=False,
                    error=f"Internal server error: {str(e)}",
                    metadata={"error_type": e.__class__.__name__}
                )
            )
    
    def list_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools with their schemas."""
        tools = {}
        for name, tool in self.tool_registry.list_tools().items():
            tools[name] = {
                "description": tool.description,
                "parameters": tool.parameters,
                "required": tool.required
            }
        return tools
