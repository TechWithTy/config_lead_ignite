"""
Service for managing messages in chat threads.
"""
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, cast
from uuid import UUID, uuid4

from ..models import (
    Message, 
    MessageType, 
    MessageStatus,
    MessageContent,
    Attachment,
    Thread,
    ParticipantRole
)
from .base import ThreadAwareService
from .thread_service import ThreadService, ParticipantService

class MessageService(ThreadAwareService[Message]):
    """Service for managing messages in chat threads."""
    
    def __init__(self, thread_service: Optional[ThreadService] = None):
        super().__init__(Message)
        self._thread_service = thread_service or ThreadService()
        self._participant_service = ParticipantService()
    
    async def create_message(
        self,
        thread_id: UUID,
        sender_id: UUID,
        content: Union[str, Dict[str, Any], MessageContent],
        message_type: MessageType = MessageType.TEXT,
        reply_to: Optional[UUID] = None,
        attachments: Optional[List[Union[Dict[str, Any], Attachment]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        sender_type: str = "user"
    ) -> Optional[Message]:
        """Create and store a new message in a thread."""
        # Verify thread exists
        thread = await self._thread_service.get(thread_id)
        if not thread:
            return None
            
        # Verify sender is a participant
        if sender_type == "user":
            participant = await self._participant_service.get_by_thread_and_user(
                thread_id, sender_id
            )
            if not participant:
                return None
        
        # Prepare message content
        if isinstance(content, str):
            content_data = MessageContent(text=content)
        elif isinstance(content, dict):
            content_data = MessageContent(**content)
        else:
            content_data = content
        
        # Prepare attachments
        attachment_objs = []
        if attachments:
            for attachment in attachments:
                if isinstance(attachment, dict):
                    attachment_objs.append(Attachment(**attachment))
                else:
                    attachment_objs.append(attachment)
        
        # Create the message
        message = Message(
            thread_id=thread_id,
            sender_id=sender_id,
            sender_type=sender_type,
            content=content_data,
            message_type=message_type,
            reply_to=reply_to,
            attachments=attachment_objs,
            metadata=metadata or {}
        )
        
        # Store the message
        created = await self.create(message)
        
        # Update thread's updated_at timestamp
        thread.updated_at = datetime.utcnow()
        await self._thread_service.update(thread.id, thread)
        
        return created
    
    async def update_message(
        self,
        message_id: UUID,
        updates: Dict[str, Any],
        user_id: Optional[UUID] = None
    ) -> Optional[Message]:
        """Update an existing message."""
        message = await self.get(message_id)
        if not message:
            return None
            
        # Check permissions if user_id is provided
        if user_id is not None and message.sender_id != user_id:
            # Check if user is an admin/moderator
            participant = await self._participant_service.get_by_thread_and_user(
                message.thread_id, user_id
            )
            if not participant or participant.role not in [ParticipantRole.ADMIN, ParticipantRole.MODERATOR]:
                return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(message, key):
                setattr(message, key, value)
        
        message.updated_at = datetime.utcnow()
        return await self.update(message_id, message)
    
    async def delete_message(
        self,
        message_id: UUID,
        user_id: Optional[UUID] = None
    ) -> bool:
        """Delete a message."""
        message = await self.get(message_id)
        if not message:
            return False
            
        # Check permissions if user_id is provided
        if user_id is not None:
            # Allow deletion by sender
            if message.sender_id == user_id and message.sender_type == "user":
                pass  # Sender can delete their own messages
            else:
                # Check if user is an admin/moderator
                participant = await self._participant_service.get_by_thread_and_user(
                    message.thread_id, user_id
                )
                if not participant or participant.role not in [ParticipantRole.ADMIN, ParticipantRole.MODERATOR]:
                    return False
        
        return await self.delete(message_id)
    
    async def list_by_thread(
        self,
        thread_id: UUID,
        limit: int = 50,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        **filters
    ) -> List[Message]:
        """List messages in a thread with pagination and filtering."""
        messages = await self.list(thread_id=thread_id, **filters)
        
        # Apply time-based filtering
        if before:
            messages = [m for m in messages if m.created_at < before]
        if after:
            messages = [m for m in messages if m.created_at > after]
        
        # Sort by creation time (newest first)
        messages.sort(key=lambda m: m.created_at, reverse=True)
        
        # Apply limit
        return messages[:limit]
    
    async def count_by_thread(self, thread_id: UUID, **filters) -> int:
        """Count messages in a thread with optional filtering."""
        return await self.count(thread_id=thread_id, **filters)
    
    async def add_reaction(
        self,
        message_id: UUID,
        user_id: UUID,
        emoji: str
    ) -> Optional[Message]:
        """Add a reaction to a message."""
        message = await self.get(message_id)
        if not message:
            return None
            
        # Initialize reactions dict if it doesn't exist
        if 'reactions' not in message.metadata:
            message.metadata['reactions'] = {}
            
        # Initialize emoji list if it doesn't exist
        if emoji not in message.metadata['reactions']:
            message.metadata['reactions'][emoji] = []
            
        # Add user to reaction if not already there
        if user_id not in message.metadata['reactions'][emoji]:
            message.metadata['reactions'][emoji].append(user_id)
            
        return await self.update(message_id, message)
    
    async def remove_reaction(
        self,
        message_id: UUID,
        user_id: UUID,
        emoji: str
    ) -> Optional[Message]:
        """Remove a reaction from a message."""
        message = await self.get(message_id)
        if not message or 'reactions' not in message.metadata:
            return None
            
        if emoji in message.metadata['reactions']:
            # Remove user from reaction
            message.metadata['reactions'][emoji] = [
                uid for uid in message.metadata['reactions'][emoji]
                if uid != user_id
            ]
            
            # Remove emoji if no more reactions
            if not message.metadata['reactions'][emoji]:
                del message.metadata['reactions'][emoji]
                
        return await self.update(message_id, message)


class MessageSearchService:
    """Service for searching messages across threads."""
    
    def __init__(self, message_service: Optional[MessageService] = None):
        self._message_service = message_service or MessageService()
    
    async def search(
        self,
        query: str,
        thread_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        limit: int = 20,
        **filters
    ) -> List[Message]:
        """Search for messages matching the query."""
        # In a real implementation, this would use a search engine like Elasticsearch
        # For now, we'll do a simple text search in memory
        
        # Get messages based on filters
        if thread_id:
            messages = await self._message_service.list_by_thread(thread_id, **filters)
        else:
            messages = await self._message_service.list(**filters)
        
        # Simple case-insensitive text search
        query = query.lower()
        results = []
        
        for message in messages:
            # Skip if user_id is provided and doesn't match
            if user_id is not None and message.sender_id != user_id:
                continue
                
            # Search in message content
            if message.content.text and query in message.content.text.lower():
                results.append(message)
            # Search in attachments (filenames)
            elif any(attachment.name and query in attachment.name.lower() 
                    for attachment in message.attachments):
                results.append(message)
            # Search in metadata
            elif any(query in str(value).lower() 
                    for value in message.metadata.values() 
                    if isinstance(value, str)):
                results.append(message)
            
            # Stop if we've reached the limit
            if len(results) >= limit:
                break
        
        return results
