"""
Base service classes for AI chat threads.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from ..models import BaseModelWithTimestamps

T = TypeVar('T', bound=BaseModelWithTimestamps)

class BaseService(ABC, Generic[T]):
    """Base service class with common CRUD operations."""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self._storage: Dict[UUID, T] = {}
    
    async def get(self, id: UUID) -> Optional[T]:
        """Retrieve a single item by ID."""
        return self._storage.get(id)
    
    async def list(self, **filters) -> List[T]:
        """List items with optional filtering."""
        results = list(self._storage.values())
        
        # Apply filters
        if filters:
            results = [
                item for item in results
                if all(
                    getattr(item, key) == value 
                    for key, value in filters.items()
                )
            ]
            
        return results
    
    async def create(self, data: Union[Dict[str, Any], T]) -> T:
        """Create a new item."""
        if isinstance(data, dict):
            item = self.model_class(**data)
        else:
            item = data
            
        self._storage[item.id] = item
        return item
    
    async def update(self, id: UUID, data: Union[Dict[str, Any], T]) -> Optional[T]:
        """Update an existing item."""
        if id not in self._storage:
            return None
            
        if isinstance(data, dict):
            # Update with dictionary
            item = self._storage[id]
            for key, value in data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
        else:
            # Replace the entire item
            self._storage[id] = data
            item = data
            
        return item
    
    async def delete(self, id: UUID) -> bool:
        """Delete an item by ID."""
        if id in self._storage:
            del self._storage[id]
            return True
        return False
    
    async def exists(self, id: UUID) -> bool:
        """Check if an item with the given ID exists."""
        return id in self._storage
    
    async def count(self, **filters) -> int:
        """Count items with optional filtering."""
        items = await self.list(**filters)
        return len(items)


class ThreadAwareService(BaseService[T], ABC):
    """Base service for services that work within the context of a thread."""
    
    @abstractmethod
    async def list_by_thread(self, thread_id: UUID, **filters) -> List[T]:
        """List items for a specific thread."""
        pass
    
    @abstractmethod
    async def count_by_thread(self, thread_id: UUID, **filters) -> int:
        """Count items for a specific thread."""
        pass
