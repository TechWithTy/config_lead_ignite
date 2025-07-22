"""
Service for managing chat threads and participants.
"""
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from ..models import (
    Thread, 
    Participant, 
    ParticipantRole,
    AIThreadParticipant,
    AIProfile
)
from .base import BaseService, ThreadAwareService

class ThreadService(BaseService[Thread]):
    """Service for managing chat threads."""
    
    def __init__(self):
        super().__init__(Thread)
        self._participant_service = ParticipantService()
        self._ai_participant_service = AIParticipantService()
    
    async def create_thread(
        self,
        creator_id: UUID,
        title: Optional[str] = None,
        is_group: bool = False,
        is_public: bool = False,
        participant_ids: Optional[List[UUID]] = None,
        ai_profile_ids: Optional[List[UUID]] = None,
        **kwargs
    ) -> Thread:
        """Create a new thread with the creator as a participant."""
        # Create the thread
        thread_data = {
            'title': title,
            'is_group': is_group,
            'is_public': is_public,
            **kwargs
        }
        thread = await self.create(thread_data)
        
        # Add creator as admin
        await self._participant_service.add_participant(
            thread_id=thread.id,
            user_id=creator_id,
            role=ParticipantRole.ADMIN
        )
        
        # Add other participants
        if participant_ids:
            for user_id in participant_ids:
                if user_id != creator_id:  # Don't add creator again
                    await self._participant_service.add_participant(
                        thread_id=thread.id,
                        user_id=user_id,
                        role=ParticipantRole.USER
                    )
        
        # Add AI participants
        if ai_profile_ids:
            for ai_profile_id in ai_profile_ids:
                await self._ai_participant_service.add_ai_participant(
                    thread_id=thread.id,
                    ai_profile_id=ai_profile_id
                )
        
        return await self.get(thread.id)
    
    async def get_thread_with_participants(self, thread_id: UUID) -> Optional[Dict]:
        """Get a thread with its participants."""
        thread = await self.get(thread_id)
        if not thread:
            return None
            
        participants = await self._participant_service.list_by_thread(thread_id)
        ai_participants = await self._ai_participant_service.list_by_thread(thread_id)
        
        return {
            **thread.model_dump(),
            'participants': [p.model_dump() for p in participants],
            'ai_participants': [ap.model_dump() for ap in ai_participants]
        }
    
    async def add_participant(
        self,
        thread_id: UUID,
        user_id: UUID,
        role: ParticipantRole = ParticipantRole.USER,
        **kwargs
    ) -> Optional[Participant]:
        """Add a participant to a thread."""
        return await self._participant_service.add_participant(
            thread_id=thread_id,
            user_id=user_id,
            role=role,
            **kwargs
        )
    
    async def remove_participant(self, thread_id: UUID, user_id: UUID) -> bool:
        """Remove a participant from a thread."""
        return await self._participant_service.remove_participant(thread_id, user_id)
    
    async def update_participant_role(
        self,
        thread_id: UUID,
        user_id: UUID,
        role: ParticipantRole
    ) -> bool:
        """Update a participant's role in a thread."""
        return await self._participant_service.update_role(thread_id, user_id, role)
    
    async def add_ai_participant(
        self,
        thread_id: UUID,
        ai_profile_id: UUID,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Optional[AIThreadParticipant]:
        """Add an AI participant to a thread."""
        return await self._ai_participant_service.add_ai_participant(
            thread_id=thread_id,
            ai_profile_id=ai_profile_id,
            config_overrides=config_overrides
        )
    
    async def remove_ai_participant(
        self,
        thread_id: UUID,
        ai_profile_id: UUID
    ) -> bool:
        """Remove an AI participant from a thread."""
        return await self._ai_participant_service.remove_ai_participant(
            thread_id=thread_id,
            ai_profile_id=ai_profile_id
        )


class ParticipantService(ThreadAwareService[Participant]):
    """Service for managing thread participants."""
    
    def __init__(self):
        super().__init__(Participant)
    
    async def add_participant(
        self,
        thread_id: UUID,
        user_id: UUID,
        role: ParticipantRole = ParticipantRole.USER,
        **kwargs
    ) -> Optional[Participant]:
        """Add a participant to a thread if they're not already a member."""
        # Check if user is already a participant
        existing = await self.get_by_thread_and_user(thread_id, user_id)
        if existing:
            return existing
            
        participant = Participant(
            thread_id=thread_id,
            user_id=user_id,
            role=role,
            **kwargs
        )
        
        return await self.create(participant)
    
    async def get_by_thread_and_user(
        self,
        thread_id: UUID,
        user_id: UUID
    ) -> Optional[Participant]:
        """Get a participant by thread ID and user ID."""
        participants = await self.list(thread_id=thread_id, user_id=user_id)
        return participants[0] if participants else None
    
    async def remove_participant(self, thread_id: UUID, user_id: UUID) -> bool:
        """Remove a participant from a thread."""
        participant = await self.get_by_thread_and_user(thread_id, user_id)
        if not participant:
            return False
            
        return await self.delete(participant.id)
    
    async def update_role(
        self,
        thread_id: UUID,
        user_id: UUID,
        role: ParticipantRole
    ) -> bool:
        """Update a participant's role in a thread."""
        participant = await self.get_by_thread_and_user(thread_id, user_id)
        if not participant:
            return False
            
        participant.role = role
        await self.update(participant.id, participant)
        return True
    
    async def list_by_thread(self, thread_id: UUID, **filters) -> List[Participant]:
        """List participants in a thread."""
        return await self.list(thread_id=thread_id, **filters)
    
    async def count_by_thread(self, thread_id: UUID, **filters) -> int:
        """Count participants in a thread."""
        return await self.count(thread_id=thread_id, **filters)


class AIParticipantService(ThreadAwareService[AIThreadParticipant]):
    """Service for managing AI participants in threads."""
    
    def __init__(self):
        super().__init__(AIThreadParticipant)
        self._ai_profile_service = AIProfileService()
    
    async def add_ai_participant(
        self,
        thread_id: UUID,
        ai_profile_id: UUID,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Optional[AIThreadParticipant]:
        """Add an AI participant to a thread."""
        # Check if AI profile exists
        ai_profile = await self._ai_profile_service.get(ai_profile_id)
        if not ai_profile:
            return None
            
        # Check if AI is already a participant
        existing = await self.get_by_thread_and_ai(thread_id, ai_profile_id)
        if existing:
            return existing
            
        participant = AIThreadParticipant(
            thread_id=thread_id,
            ai_profile_id=ai_profile_id,
            config_overrides=config_overrides or {}
        )
        
        return await self.create(participant)
    
    async def get_by_thread_and_ai(
        self,
        thread_id: UUID,
        ai_profile_id: UUID
    ) -> Optional[AIThreadParticipant]:
        """Get an AI participant by thread ID and AI profile ID."""
        participants = await self.list(thread_id=thread_id, ai_profile_id=ai_profile_id)
        return participants[0] if participants else None
    
    async def remove_ai_participant(
        self,
        thread_id: UUID,
        ai_profile_id: UUID
    ) -> bool:
        """Remove an AI participant from a thread."""
        participant = await self.get_by_thread_and_ai(thread_id, ai_profile_id)
        if not participant:
            return False
            
        return await self.delete(participant.id)
    
    async def update_config_overrides(
        self,
        thread_id: UUID,
        ai_profile_id: UUID,
        config_overrides: Dict[str, Any]
    ) -> bool:
        """Update an AI participant's configuration overrides."""
        participant = await self.get_by_thread_and_ai(thread_id, ai_profile_id)
        if not participant:
            return False
            
        participant.config_overrides = config_overrides
        await self.update(participant.id, participant)
        return True
    
    async def list_by_thread(self, thread_id: UUID, **filters) -> List[AIThreadParticipant]:
        """List AI participants in a thread."""
        return await self.list(thread_id=thread_id, **filters)
    
    async def count_by_thread(self, thread_id: UUID, **filters) -> int:
        """Count AI participants in a thread."""
        return await self.count(thread_id=thread_id, **filters)


class AIProfileService(BaseService[AIProfile]):
    """Service for managing AI profiles."""
    
    def __init__(self):
        super().__init__(AIProfile)
    
    async def get_by_user(self, user_id: UUID) -> List[AIProfile]:
        """Get all AI profiles for a user."""
        return await self.list(user_id=user_id)
    
    async def get_public_profiles(self) -> List[AIProfile]:
        """Get all public AI profiles."""
        return await self.list(is_public=True)
