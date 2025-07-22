"""
Example A2A Agent Implementation

This module demonstrates how to create and use an A2A agent with custom capabilities.
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import FastAPI
import uvicorn

from .models import (
    A2AMessage,
    MessageType,
    Task,
    TaskStatus,
    MessagePart,
    ContentType,
    AgentCard
)
from .service import A2AService
from .router import register_a2a_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExampleAgent:
    """An example A2A agent with sample capabilities."""
    
    def __init__(self, agent_id: str, agent_name: str, port: int = 8000):
        """Initialize the example agent.
        
        Args:
            agent_id: Unique identifier for this agent
            agent_name: Human-readable name for this agent
            port: Port to run the FastAPI server on
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.port = port
        
        # Initialize the A2A service
        self.a2a_service = A2AService(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_description=f"An example A2A agent: {agent_name}"
        )
        
        # Register capabilities
        self._register_capabilities()
        
        # Initialize FastAPI app
        self.app = FastAPI(title=f"{agent_name} (A2A Agent)")
        
        # Register A2A routes
        register_a2a_routes(self.app)
        
        # Store active tasks
        self.active_tasks: Dict[UUID, Dict[str, Any]] = {}
    
    def _register_capabilities(self) -> None:
        """Register this agent's capabilities."""
        # Example capability: Text summarization
        self.a2a_service.register_capability(
            name="summarize_text",
            description="Summarize a given text",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to summarize"},
                    "max_length": {"type": "integer", "description": "Maximum length of the summary"}
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "The generated summary"},
                    "original_length": {"type": "integer", "description": "Length of the original text"},
                    "summary_length": {"type": "integer", "description": "Length of the summary"}
                }
            }
        )
        
        # Example capability: Sentiment analysis
        self.a2a_service.register_capability(
            name="analyze_sentiment",
            description="Analyze the sentiment of a given text",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to analyze"}
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"], "description": "The detected sentiment"},
                    "confidence": {"type": "number", "description": "Confidence score between 0 and 1"},
                    "tokens_analyzed": {"type": "integer", "description": "Number of tokens analyzed"}
                }
            }
        )
        
        # Register task handlers
        self.a2a_service.register_task_handler("summarize_text", self._handle_summarize_text)
        self.a2a_service.register_task_handler("analyze_sentiment", self._handle_analyze_sentiment)
        
        # Register message handlers
        self.a2a_service.register_message_handler(
            MessageType.MESSAGE,
            self._handle_general_message
        )
    
    async def _handle_summarize_text(self, task: Task) -> Dict[str, Any]:
        """Handle text summarization tasks.
        
        This is a simple implementation that just takes the first few sentences.
        In a real application, you would use a proper summarization model.
        """
        text = task.parameters.get("text", "")
        max_length = task.parameters.get("max_length", 200)
        
        # Simple summarization: take first few sentences
        sentences = text.split(". ")
        summary = ". ".join(sentences[:3]) + "."
        
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary)
        }
    
    async def _handle_analyze_sentiment(self, task: Task) -> Dict[str, Any]:
        """Handle sentiment analysis tasks.
        
        This is a simple implementation that does basic sentiment analysis.
        In a real application, you would use a proper sentiment analysis model.
        """
        text = task.parameters.get("text", "").lower()
        
        # Simple sentiment analysis
        positive_words = ["good", "great", "excellent", "awesome", "happy"]
        negative_words = ["bad", "terrible", "awful", "horrible", "sad"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count * 0.1))
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "tokens_analyzed": len(text.split())
        }
    
    async def _handle_general_message(self, message: A2AMessage) -> None:
        """Handle general messages from other agents."""
        logger.info(f"Received message from {message.sender_id}: {message.parts[0].content if message.parts else 'No content'}")
        
        # Echo the message back to the sender
        if message.sender_id != self.agent_id:  # Avoid infinite loops
            await self.a2a_service.send_message(
                recipient_id=message.sender_id,
                message_type=MessageType.MESSAGE,
                parts=[
                    MessagePart(
                        content_type=ContentType.TEXT,
                        content=f"Echo from {self.agent_name}: {message.parts[0].content if message.parts else 'Hello!'}"
                    )
                ],
                conversation_id=message.conversation_id
            )
    
    def run(self):
        """Run the agent's FastAPI server."""
        logger.info(f"Starting {self.agent_name} on port {self.port}")
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )

async def example_agent_interaction():
    """Example of how two agents can interact using the A2A protocol."""
    # Create two agents
    agent1 = ExampleAgent("agent1", "Example Agent 1", port=8000)
    agent2 = ExampleAgent("agent2", "Example Agent 2", port=8001)
    
    # Start the agents in separate processes (in a real application)
    # For this example, we'll just demonstrate the API usage
    
    # Agent 1 sends a message to Agent 2
    message = await agent1.a2a_service.send_message(
        recipient_id="agent2",
        message_type=MessageType.MESSAGE,
        parts=[
            MessagePart(
                content_type=ContentType.TEXT,
                content="Hello from Agent 1!"
            )
        ]
    )
    
    print(f"Agent 1 sent message: {message.parts[0].content}")
    
    # Agent 1 asks Agent 2 to summarize some text
    task = await agent1.a2a_service.execute_task(
        capability_name="summarize_text",
        parameters={
            "text": """
            The A2A protocol is a new standard for agent interoperability. 
            It allows different AI agents to discover each other's capabilities, 
            exchange messages, and collaborate on tasks. This enables more 
            complex and powerful AI applications by combining the strengths 
            of multiple specialized agents.
            """,
            "max_length": 100
        },
        recipient_id="agent2"
    )
    
    print(f"Agent 2 summarized text: {task.result['summary']}")

if __name__ == "__main__":
    # Run the example agent interaction
    # asyncio.run(example_agent_interaction())
    
    # Or run a single agent
    agent = ExampleAgent("example_agent", "Example Agent")
    agent.run()
