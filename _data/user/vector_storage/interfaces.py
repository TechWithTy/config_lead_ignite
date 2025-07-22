from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class VectorDatabase(ABC):
    """Abstract base class for vector database operations"""
    
    @abstractmethod
    async def create_collection(self, collection: Any) -> Dict[str, Any]:
        """Create a new vector collection"""
        pass
    
    @abstractmethod
    async def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector collection by ID"""
        pass
    
    @abstractmethod
    async def add_embeddings(
        self, 
        collection_id: str,
        embeddings: List[Any]
    ) -> List[Dict[str, Any]]:
        """Add multiple embeddings to a collection"""
        pass
    
    @abstractmethod
    async def search_similar(
        self,
        collection_id: str,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in a collection"""
        pass
    
    @abstractmethod
    async def create_index(
        self, 
        collection_id: str, 
        index_type: str = "ivfflat",
        index_params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a vector index for a collection"""
        pass
    
    @abstractmethod
    async def update_collection(
        self, 
        collection_id: str, 
        **updates
    ) -> Optional[Dict[str, Any]]:
        """Update a collection's properties"""
        pass
