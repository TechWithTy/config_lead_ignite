"""
FastAPI router for A2A (Agent-to-Agent) protocol endpoints.
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .models import (
    A2AMessage,
    AgentCard,
    MessageType,
    Task,
    TaskStatus,
    MessagePart,
    ContentType
)
from .service import A2AService
from .exceptions import A2AError, AgentNotFoundError, InvalidMessageError, TaskNotFoundError

# Create router
router = APIRouter(
    prefix="/a2a",
    tags=["a2a"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get A2A service
def get_a2a_service() -> A2AService:
    """Get A2A service instance.
    
    In a real application, you would get the service from your dependency injection system.
    This is a simplified version that creates a new instance each time.
    """
    # TODO: Replace with your actual service initialization
    service = A2AService(
        agent_id="example_agent",
        agent_name="Example Agent",
        agent_description="An example A2A agent"
    )
    return service

# Request/Response Models
class MessageRequest(BaseModel):
    """Request model for sending a message."""
    recipient_id: str
    message_type: str
    parts: List[Dict[str, Any]]
    conversation_id: Optional[str] = None
    task: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskRequest(BaseModel):
    """Request model for executing a task."""
    capability_name: str
    parameters: Dict[str, Any]
    recipient_id: str
    timeout: Optional[float] = 60.0

class StatusUpdateRequest(BaseModel):
    """Request model for updating task status."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# Endpoints
@router.post("/messages", response_model=Dict[str, Any])
async def send_message(
    request: Request,
    message_req: MessageRequest,
    a2a_service: A2AService = Depends(get_a2a_service)
) -> Dict[str, Any]:
    """
    Send a message to another agent.
    
    This endpoint allows agents to send messages to each other using the A2A protocol.
    """
    try:
        # Convert parts to MessagePart objects
        parts = [
            MessagePart(
                content_type=ContentType(part.get("content_type", "text/plain")),
                content=part["content"],
                name=part.get("name"),
                metadata=part.get("metadata", {})
            )
            for part in message_req.parts
        ]
        
        # Convert task if provided
        task = None
        if message_req.task:
            task = Task(**message_req.task)
        
        # Send the message
        message = await a2a_service.send_message(
            recipient_id=message_req.recipient_id,
            message_type=MessageType(message_req.message_type),
            parts=parts,
            conversation_id=message_req.conversation_id,
            task=task,
            metadata=message_req.metadata or {}
        )
        
        return {
            "success": True,
            "message_id": str(message.message_id),
            "conversation_id": str(message.conversation_id),
            "timestamp": message.timestamp.isoformat()
        }
        
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except A2AError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/tasks", response_model=Dict[str, Any])
async def execute_task(
    request: Request,
    task_req: TaskRequest,
    a2a_service: A2AService = Depends(get_a2a_service)
) -> Dict[str, Any]:
    """
    Execute a task on another agent.
    
    This endpoint allows agents to request the execution of a task by another agent
    that provides the specified capability.
    """
    try:
        # Execute the task
        task = await a2a_service.execute_task(
            capability_name=task_req.capability_name,
            parameters=task_req.parameters,
            recipient_id=task_req.recipient_id,
            timeout=task_req.timeout
        )
        
        # Prepare the response
        response = {
            "task_id": str(task.task_id),
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "result": task.result,
            "error": task.error,
            "metadata": task.metadata
        }
        
        return {
            "success": task.status == TaskStatus.COMPLETED,
            "data": response
        }
        
    except (AgentNotFoundError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/capabilities", response_model=Dict[str, Any])
async def get_capabilities(
    request: Request,
    a2a_service: A2AService = Depends(get_a2a_service)
) -> Dict[str, Any]:
    """
    Get the capabilities of this agent.
    
    This endpoint returns the agent's capabilities in the form of an AgentCard.
    """
    try:
        agent_card = a2a_service.get_agent_card()
        return {
            "success": True,
            "data": agent_card.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get capabilities: {str(e)}"
        )

@router.post("/status", response_model=Dict[str, Any])
async def update_task_status(
    request: Request,
    status_req: StatusUpdateRequest,
    a2a_service: A2AService = Depends(get_a2a_service)
) -> Dict[str, Any]:
    """
    Update the status of a task.
    
    This endpoint allows agents to update the status of a task, including
    providing results or error information.
    """
    try:
        # Send status update
        await a2a_service.send_status_update(
            task_id=status_req.task_id,
            status=TaskStatus(status_req.status),
            recipient_id=request.headers.get("X-Agent-ID", "unknown"),
            conversation_id=request.headers.get("X-Conversation-ID"),
            result=status_req.result,
            error=status_req.error
        )
        
        return {
            "success": True,
            "message": f"Task {status_req.task_id} status updated to {status_req.status}"
        }
        
    except (ValueError, TaskNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task status: {str(e)}"
        )

# Webhook endpoint for receiving messages
@router.post("/webhook")
async def webhook(
    request: Request,
    a2a_service: A2AService = Depends(get_a2a_service)
) -> Dict[str, Any]:
    """
    Webhook endpoint for receiving A2A messages.
    
    This endpoint receives messages from other agents and processes them.
    """
    try:
        # Parse the incoming message
        data = await request.json()
        
        # Process the message
        await a2a_service.process_message(data)
        
        return {
            "success": True,
            "message": "Message received and processed"
        }
        
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message format: {str(e)}"
        )
    except A2AError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

def register_a2a_routes(app):
    """Register A2A routes with the FastAPI application."""
    app.include_router(router)
    return app
