"""
A2A (Agent-to-Agent) Service

This module implements the core service for handling A2A protocol communications
between agents, including task management, message routing, and capability discovery.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from .models import (
    A2AMessage,
    A2AResponse,
    MessageType,
    Task,
    TaskStatus,
    AgentCard,
    AgentCapability,
    ContentType,
    MessagePart
)
from .exceptions import A2AError, AgentNotFoundError, InvalidMessageError, TaskNotFoundError

logger = logging.getLogger(__name__)

# Type aliases
MessageHandler = Callable[[A2AMessage], Awaitable[None]]
TaskHandler = Callable[[Task], Awaitable[Task]]

class A2AService:
    """Core service for A2A protocol implementation."""
    
    def __init__(self, agent_id: str, agent_name: str, agent_description: str):
        """Initialize the A2A service.
        
        Args:
            agent_id: Unique identifier for this agent
            agent_name: Human-readable name of the agent
            agent_description: Description of the agent's purpose
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_description = agent_description
        
        # Agent capabilities and handlers
        self.capabilities: Dict[str, AgentCapability] = {}
        self.message_handlers: Dict[MessageType, List[MessageHandler]] = {}
        self.task_handlers: Dict[str, TaskHandler] = {}
        
        # Active tasks and conversations
        self.active_tasks: Dict[UUID, Task] = {}
        self.conversations: Dict[UUID, List[A2AMessage]] = {}
        
        # Agent registry (in a real implementation, this would be a separate service)
        self.known_agents: Dict[str, AgentCard] = {}
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default message and task handlers."""
        self.register_message_handler(MessageType.CAPABILITY_DISCOVERY, self._handle_capability_discovery)
        self.register_message_handler(MessageType.STATUS_UPDATE, self._handle_status_update)
    
    async def _handle_capability_discovery(self, message: A2AMessage) -> None:
        """Handle capability discovery requests."""
        if message.sender_id not in self.known_agents:
            # In a real implementation, we would discover the agent's capabilities
            # For now, we'll just acknowledge the message
            pass
        
        # Send our capabilities back to the sender
        await self.send_message(
            recipient_id=message.sender_id,
            message_type=MessageType.CAPABILITY_DISCOVERY,
            parts=[
                MessagePart(
                    content_type=ContentType.JSON,
                    content=json.dumps(self.get_agent_card().dict())
                )
            ],
            conversation_id=message.conversation_id
        )
    
    async def _handle_status_update(self, message: A2AMessage) -> None:
        """Handle task status updates from other agents."""
        if not message.task:
            raise InvalidMessageError("Status update message must include a task")
        
        task_id = message.task.task_id
        if task_id in self.active_tasks:
            self.active_tasks[task_id].status = message.task.status
            self.active_tasks[task_id].updated_at = datetime.utcnow()
            
            if message.task.result:
                self.active_tasks[task_id].result = message.task.result
            if message.task.error:
                self.active_tasks[task_id].error = message.task.error
    
    def get_agent_card(self) -> AgentCard:
        """Get this agent's capability card."""
        return AgentCard(
            agent_id=self.agent_id,
            name=self.agent_name,
            description=self.agent_description,
            capabilities=list(self.capabilities.values())
        )
    
    def register_capability(
        self,
        name: str,
        description: str,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a capability that this agent provides.
        
        Args:
            name: Name of the capability
            description: Description of what the capability does
            input_schema: JSON Schema for input parameters
            output_schema: JSON Schema for output data
            metadata: Additional metadata about the capability
        """
        self.capabilities[name] = AgentCapability(
            name=name,
            description=description,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            metadata=metadata or {}
        )
    
    def register_message_handler(
        self,
        message_type: MessageType,
        handler: MessageHandler
    ) -> None:
        """Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function that processes the message
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def register_task_handler(
        self,
        capability_name: str,
        handler: TaskHandler
    ) -> None:
        """Register a handler for a specific task type.
        
        Args:
            capability_name: Name of the capability this handler implements
            handler: Async function that processes the task
        """
        self.task_handlers[capability_name] = handler
    
    async def process_message(self, message: Union[Dict[str, Any], A2AMessage]) -> None:
        """Process an incoming A2A message.
        
        Args:
            message: The incoming message as a dict or A2AMessage instance
            
        Raises:
            InvalidMessageError: If the message is malformed
        """
        # Parse the message if it's a dict
        if isinstance(message, dict):
            try:
                message = A2AMessage(**message)
            except Exception as e:
                raise InvalidMessageError(f"Invalid message format: {str(e)}")
        
        # Store the message in the conversation history
        if message.conversation_id not in self.conversations:
            self.conversations[message.conversation_id] = []
        self.conversations[message.conversation_id].append(message)
        
        # Handle the message based on its type
        if message.message_type in self.message_handlers:
            for handler in self.message_handlers[message.message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {str(e)}", exc_info=True)
        
        # If this is a task message, handle the task
        if message.task and message.message_type == MessageType.TASK:
            await self._handle_task(message)
    
    async def _handle_task(self, message: A2AMessage) -> None:
        """Handle an incoming task message."""
        if not message.task:
            return
        
        task = message.task
        self.active_tasks[task.task_id] = task
        
        # Find a handler for this task
        handler = None
        for capability_name in self.capabilities:
            if capability_name in task.parameters:
                handler = self.task_handlers.get(capability_name)
                if handler:
                    break
        
        if not handler:
            # No handler found for this task
            task.status = TaskStatus.FAILED
            task.error = {"error": "No suitable handler found for this task"}
            task.updated_at = datetime.utcnow()
            return
        
        try:
            # Update task status to in progress
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.utcnow()
            
            # Send status update
            await self.send_status_update(
                task_id=task.task_id,
                status=TaskStatus.IN_PROGRESS,
                recipient_id=message.sender_id,
                conversation_id=message.conversation_id
            )
            
            # Execute the task
            result = await handler(task)
            
            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.result = result.dict() if hasattr(result, 'dict') else result
            task.updated_at = datetime.utcnow()
            
            # Send completion status
            await self.send_status_update(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=task.result,
                recipient_id=message.sender_id,
                conversation_id=message.conversation_id
            )
            
        except Exception as e:
            # Handle task execution error
            task.status = TaskStatus.FAILED
            task.error = {"error": str(e), "type": e.__class__.__name__}
            task.updated_at = datetime.utcnow()
            
            # Send error status
            await self.send_status_update(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=task.error,
                recipient_id=message.sender_id,
                conversation_id=message.conversation_id
            )
            
            logger.error(f"Error executing task {task.task_id}: {str(e)}", exc_info=True)
    
    async def send_message(
        self,
        recipient_id: str,
        message_type: MessageType,
        parts: List[MessagePart],
        conversation_id: Optional[UUID] = None,
        task: Optional[Task] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> A2AMessage:
        """Send a message to another agent.
        
        Args:
            recipient_id: ID of the recipient agent
            message_type: Type of the message
            parts: Message content parts
            conversation_id: Optional conversation ID (will create a new one if not provided)
            task: Optional task associated with the message
            metadata: Additional metadata
            
        Returns:
            The sent message
            
        Note: In a real implementation, this would send the message over the network
        to the recipient agent. This is a simplified version that just logs the message.
        """
        message = A2AMessage(
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            parts=parts,
            task=task,
            metadata=metadata or {},
            conversation_id=conversation_id or uuid4()
        )
        
        # In a real implementation, we would send this message over the network
        logger.info(f"Sending message to {recipient_id}: {message_type}")
        logger.debug(f"Message details: {message.json(indent=2)}")
        
        return message
    
    async def send_status_update(
        self,
        task_id: UUID,
        status: TaskStatus,
        recipient_id: str,
        conversation_id: UUID,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send a task status update to another agent.
        
        Args:
            task_id: ID of the task
            status: New status of the task
            recipient_id: ID of the recipient agent
            conversation_id: Conversation ID
            result: Optional task result
            error: Optional error details
        """
        task = self.active_tasks.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        # Update task status
        task.status = status
        task.updated_at = datetime.utcnow()
        
        if result is not None:
            task.result = result
        if error is not None:
            task.error = error
        
        # Send status update message
        await self.send_message(
            recipient_id=recipient_id,
            message_type=MessageType.STATUS_UPDATE,
            parts=[
                MessagePart(
                    content_type=ContentType.JSON,
                    content=json.dumps({
                        "task_id": str(task_id),
                        "status": status.value,
                        "result": result,
                        "error": error
                    })
                )
            ],
            conversation_id=conversation_id,
            task=task
        )
    
    async def execute_task(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        recipient_id: str,
        timeout: float = 60.0
    ) -> Task:
        """Execute a task on another agent and wait for the result.
        
        Args:
            capability_name: Name of the capability to execute
            parameters: Parameters for the task
            recipient_id: ID of the agent to execute the task
            timeout: Maximum time to wait for the task to complete (in seconds)
            
        Returns:
            The completed task with result
            
        Raises:
            TimeoutError: If the task times out
            AgentNotFoundError: If the recipient agent is not found
        """
        if recipient_id not in self.known_agents:
            raise AgentNotFoundError(f"Agent {recipient_id} not found")
        
        # Create a new task
        task = Task(
            parameters=parameters,
            metadata={"requested_capability": capability_name}
        )
        
        # Send task message
        message = await self.send_message(
            recipient_id=recipient_id,
            message_type=MessageType.TASK,
            parts=[
                MessagePart(
                    content_type=ContentType.JSON,
                    content=json.dumps({"capability": capability_name})
                )
            ],
            task=task
        )
        
        # Wait for task completion
        start_time = datetime.utcnow()
        while True:
            # Check for timeout
            if (datetime.utcnow() - start_time).total_seconds() > timeout:
                task.status = TaskStatus.FAILED
                task.error = {"error": "Task timed out"}
                task.updated_at = datetime.utcnow()
                raise TimeoutError(f"Task {task.task_id} timed out after {timeout} seconds")
            
            # Check task status
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                break
                
            # Wait before checking again
            await asyncio.sleep(0.1)
        
        return task
